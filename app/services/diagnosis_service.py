import os
import cv2
import numpy as np
import base64
import uuid
import io
import asyncio
from pathlib import Path
from datetime import datetime

import httpx
from ultralytics import YOLO
from fastapi import UploadFile
from sqlalchemy.orm import Session
from PIL import Image, ImageOps

from app.core.config import settings
from app.crud import crud_diagonsis

# Threshold for calculating wrinkle score 
MAX_WRINKLE_RATIO_THRESHOLD = 0.1 

# Relative path to the current file directory
CURRENT_FILE_DIR = Path(__file__).resolve().parent

def calculate_score(masks: np.ndarray) -> int:
    """
    Calculates a score (0-100) based on YOLO mask data.
    100 = No issue detected.
    0 = Issue covers >= MAX_WRINKLE_RATIO_THRESHOLD of the image.
    """
    if masks is None or masks.size == 0:
        return 100  # No masks detected, perfect score

    combined_mask = np.any(masks, axis=0)
    white_pixels = np.sum(combined_mask)
    total_pixels = combined_mask.shape[0] * combined_mask.shape[1]

    if total_pixels == 0:
        return 100 

    ratio = white_pixels / total_pixels
    score = 100.0 * (1.0 - (ratio / MAX_WRINKLE_RATIO_THRESHOLD))
    
    return int(np.clip(score, 0, 100))


def _run_yolo_segmentation(
    img_path: str,
    output_dir: str,
    weight_path: str,
    analysis_type: str,
    img_size: int = settings.IMG_SIZE,
    device: str = settings.AI_DEVICE
) -> tuple[str | None, int]:
    """
    Returns the overlay image path and the calculated score.
    """
    if not os.path.exists(weight_path):
        raise FileNotFoundError(f"Weight not found: {weight_path}")
    
    model = YOLO(weight_path)
    results = model.predict(source=img_path, conf=0.25, imgsz=img_size, device=device, save=False, show=False)

    result = results[0]
    if result.masks is None:
        print(f"No {analysis_type} masks found.")
        return None, 100

    img_rgb = cv2.cvtColor(result.orig_img, cv2.COLOR_BGR2RGB)
    masks = result.masks.data.cpu().numpy()
    combined_mask_viz = np.zeros_like(img_rgb, dtype=np.uint8)

    for mask in masks:
        color = (255, 255, 255) # Use white for all masks
        combined_mask_viz[mask.astype(bool)] = color

    score = calculate_score(masks)
    overlay = cv2.addWeighted(img_rgb, 0.6, combined_mask_viz, 0.4, 0)
    
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{analysis_type}_{os.path.basename(img_path)}"
    output_path = os.path.join(output_dir, filename)
    
    overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, overlay_bgr)
    
    return output_path, score


def run_skin_analysis(
    image_path: str, 
    model_name: str = "llava", 
    translator_model: str = "gemma2:9b",
    analysis_type: str = "wrinkle"
) -> str:
    """
    Uses Ollama REST API (via httpx) to get skin analysis advice in Korean.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    ollama_api_url = f"{settings.OLLAMA_HOST}/api/chat"

    prompt_en = (
        "You are a friendly but professional dermatologist AI.\n"
        "You will be given a close-up image of a user's skin.\n"
        "Do not describe the image.\n"
        f"The main concern is {analysis_type} and talk to the user directly.\n"
        "Give short, natural advice as if speaking to them, in a warm but expert tone.\n"
        "Focus on 1-2 key problems and how to improve them with practical skincare steps.\n"
        "Keep it under 3 short sentences in English."
    )
    
    # LLaVA (이미지 포함) 요청 페이로드
    payload_en = {
        "model": model_name,
        "stream": False,
        "messages": [
            {"role": "system", "content": prompt_en},
            {
                "role": "user",
                "content": "Look at this skin image and give direct, short advice to the user.",
                "images": [image_base64],
            },
        ],
    }

    try:
        with httpx.Client() as client:
            response_en = client.post(ollama_api_url, json=payload_en, timeout=60.0)
            response_en.raise_for_status() 
            
            english_advice = response_en.json()["message"]["content"].strip()

            prompt_ko = (
                "Translate the following English skincare advice into fluent, natural Korean.\n"
                "Write as if speaking directly to the user.\n"
                "Use only Korean characters (no Japanese, Chinese, or English words).\n"
                "Keep it short (2-3 sentences), polite, and clear.\n"
                "Do not describe the image or add any extra explanation.\n"
                "Text to translate:\n" + english_advice
            )
            
            payload_ko = {
                "model": translator_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": "You are a professional translator."},
                    {"role": "user", "content": prompt_ko},
                ],
            }
            
            response_ko = client.post(ollama_api_url, json=payload_ko, timeout=30.0)
            response_ko.raise_for_status()
            
            return response_ko.json()["message"]["content"].strip()
    
    except httpx.HTTPStatusError as e:
        print(f"Ollama API request failed with status {e.response.status_code}: {e.response.text}")
        return f"피부 분석 중 API 오류가 발생했습니다. (모델: {analysis_type})"
    except httpx.RequestError as e:
        print(f"Error connecting to Ollama service at {e.request.url!r}: {e}")
        return f"피부 분석 중 오류가 발생했습니다. (모델: {analysis_type})"
    except Exception as e:
        print(f"An unexpected error occurred during skin analysis: {e}")
        return f"피부 분석 중 오류가 발생했습니다. (모델: {analysis_type})"


def resize_and_save_image(
    contents: bytes, 
    save_path: Path, 
    size: int = settings.IMG_SIZE
) -> None:
    """
    Resizes and crops uploaded bytes to a square image (e.g., 1024x1024) and saves it.
    """
    image = Image.open(io.BytesIO(contents))
    resized_image = ImageOps.fit(image, (size, size), Image.Resampling.LANCZOS)
    
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    if resized_image.mode == 'RGBA':
        resized_image = resized_image.convert('RGB')
        
    resized_image.save(save_path, format="JPEG", quality=95)

def _run_sync_processing(
    db: Session, 
    contents: bytes, 
    user_id: str
):
    """
    Handles all heavy, synchronous processing (IO, CPU, AI models).
    Designed to be run in a separate thread via asyncio.to_thread.
    """
    # 1. Save original image
    uid = str(uuid.uuid4())
    filename = f"{uid}.jpg"
    original_save_path = settings.STATIC_DIR / user_id / filename
    original_image_url = f"{settings.STATIC_URL_PREFIX}/{user_id}/{filename}"

    resize_and_save_image(contents, original_save_path, size=settings.IMG_SIZE)
    original_save_path_str = str(original_save_path)
    
    analysis_data = {}

    # 2. Run Wrinkle Analysis
    wrinkle_dir = str(settings.STATIC_DIR / user_id / uid / "wrinkle")
    wrinkle_weight = f"{CURRENT_FILE_DIR}/weights/wrinkle.pt"
    
    wrinkle_path, wrinkle_score = _run_yolo_segmentation(
        img_path=original_save_path_str,
        output_dir=wrinkle_dir,
        weight_path=wrinkle_weight,
        analysis_type="wrinkle",
        device=settings.AI_DEVICE
    )
    wrinkle_url = f"{settings.STATIC_URL_PREFIX}/{user_id}/{uid}/wrinkle/{Path(wrinkle_path).name}" if wrinkle_path else original_image_url
    wrinkle_desc = run_skin_analysis(image_path=original_save_path_str, analysis_type="wrinkle")

    analysis_data.update({
        "wrinkle_score": wrinkle_score,
        "wrinkle_image_url": wrinkle_url,
        "wrinkle_description": wrinkle_desc,
    })

    # 3. Run Acne Analysis
    acne_dir = str(settings.STATIC_DIR / user_id / uid / "acne")
    acne_weight = f"{CURRENT_FILE_DIR}/weights/acne.pt"
    
    acne_path, acne_score = _run_yolo_segmentation(
        img_path=original_save_path_str,
        output_dir=acne_dir,
        weight_path=acne_weight,
        analysis_type="acne",
        device=settings.AI_DEVICE
    )
    acne_url = f"{settings.STATIC_URL_PREFIX}/{user_id}/{uid}/acne/{Path(acne_path).name}" if acne_path else original_image_url
    acne_desc = run_skin_analysis(image_path=original_save_path_str, analysis_type="acne")
    
    analysis_data.update({
        "acne_score": acne_score,
        "acne_image_url": acne_url,
        "acne_description": acne_desc,
    })

    # 4. Run Atopy Analysis
    atopy_dir = str(settings.STATIC_DIR / user_id / uid / "atopy")
    atopy_weight = f"{CURRENT_FILE_DIR}/weights/atopy.pt"
    
    atopy_path, atopy_score = _run_yolo_segmentation(
        img_path=original_save_path_str,
        output_dir=atopy_dir,
        weight_path=atopy_weight,
        analysis_type="atopy",
        device=settings.AI_DEVICE
    )
    atopy_url = f"{settings.STATIC_URL_PREFIX}/{user_id}/{uid}/atopy/{Path(atopy_path).name}" if atopy_path else original_image_url
    atopy_desc = run_skin_analysis(image_path=original_save_path_str, analysis_type="atopy")

    analysis_data.update({
        "atopy_score": atopy_score,
        "atopy_image_url": atopy_url,
        "atopy_description": atopy_desc,
    })

    # 5. Calculate total score and save to DB
    total_score = (wrinkle_score + acne_score + atopy_score) // 3
    created_at = datetime.now()
    
    db_diagnosis = crud_diagonsis.create_diagnosis(
        db=db,
        user_id=user_id,
        original_image_url=original_image_url,
        created_at=created_at,
        total_score=total_score,
        **analysis_data  # ❗️ Unpack all results
    )
    return db_diagnosis


async def process_diagnosis(
    db: Session, 
    file: UploadFile, 
    user_id: str
):
    """
    Main async service function called by the endpoint.
    Reads file asynchronously, then runs all blocking 
    processing in a separate thread.
    """
    # 1. (Async) Read file contents
    contents = await file.read()
    
    # 2. (Sync in Thread) Run all blocking IO and AI tasks
    db_diagnosis = await asyncio.to_thread(
        _run_sync_processing, db, contents, user_id
    )

    return db_diagnosis