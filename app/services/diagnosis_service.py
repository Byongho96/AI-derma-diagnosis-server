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
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from PIL import Image, ImageOps

from app.core.config import settings
from app.crud import crud_diagonsis

# Threshold for calculating wrinkle score 
MAX_WRINKLE_RATIO_THRESHOLD = 0.1 

# Relative path to the current file directory
CURRENT_FILE_DIR = Path(__file__).resolve().parent

# Pre-load AI models
FACE_MODEL_PATH = f"{CURRENT_FILE_DIR}/weights/yolov8n-face-lindevs.pt"
WRINKLE_WEIGHT_PATH = f"{CURRENT_FILE_DIR}/weights/wrinkle.pt"
ACNE_WEIGHT_PATH = f"{CURRENT_FILE_DIR}/weights/acne.pt"
ATOPY_WEIGHT_PATH = f"{CURRENT_FILE_DIR}/weights/atopy.pt"

for path in [FACE_MODEL_PATH, WRINKLE_WEIGHT_PATH, ACNE_WEIGHT_PATH, ATOPY_WEIGHT_PATH]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Weight file not found: {path}")

print("Loading AI models into memory...")
FACE_MODEL = YOLO(FACE_MODEL_PATH)
WRINKLE_MODEL = YOLO(WRINKLE_WEIGHT_PATH)
ACNE_MODEL = YOLO(ACNE_WEIGHT_PATH)
ATOPY_MODEL = YOLO(ATOPY_WEIGHT_PATH)
print("All models loaded successfully.")

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
    
    if analysis_type == "wrinkle":
        model = WRINKLE_MODEL
    elif analysis_type == "acne":
        model = ACNE_MODEL
    elif analysis_type == "atopy":
        model = ATOPY_MODEL
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    results = model.predict(source=img_path, conf=0.25, imgsz=img_size, device=device, save=False, show=False)

    result = results[0]

    img_rgb = cv2.cvtColor(result.orig_img, cv2.COLOR_BGR2RGB)
    combined_mask_viz = np.zeros_like(img_rgb, dtype=np.uint8)

    if result.masks is None:
        print(f"No {analysis_type} masks found. Creating black overlay.")
        score = 100
    else:
        print(f"Found {len(result.masks)} {analysis_type} masks.")
        masks = result.masks.data.cpu().numpy()
        
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
) -> str:
    """
    Uses Ollama REST API (via httpx) to get skin analysis advice in Korean.
    """
    # return "개발 모드에서는 피부 분석 기능이 비활성화되어 있습니다."
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    ollama_api_url = f"{settings.OLLAMA_HOST}/api/chat"

    prompt_en = (
        "You are a friendly but professional dermatologist AI.\n"
        "You will be given a close-up image of a user's skin.\n"
        "Do not describe the image.\n"
        "Identify the main skin concern (like acne, wrinkle, atopy) and talk to the user directly.\n"
        "Give short, natural advice as if speaking to them, in a warm but expert tone.\n"
        "Focus on 1-2 key problems and how to improve them with practical skincare steps.\n"
        "Keep it under 3 short sentences in English."
    )
    
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
        return f"피부 LLM 분석 중 API 오류가 발생했습니다."
    except httpx.RequestError as e:
        print(f"Error connecting to Ollama service at {e.request.url!r}: {e}")
        return f"피부 LLM 분석 중 오류가 발생했습니다."
    except Exception as e:
        print(f"An unexpected error occurred during skin analysis: {e}")
        return f"피부 LLM 분석 중 오류가 발생했습니다."


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
    # Bytes -> PIL Image -> CV2 Image to run face detection with OpenCV
    try:
        pil_image = Image.open(io.BytesIO(contents))
        pil_image_rgb = pil_image.convert('RGB')
    except Exception as e:
        print(f"Image decoding failed: {e}")
        raise HTTPException(status_code=400, detail="이미지 파일을 처리할 수 없습니다.")

    # Face detection
    results = FACE_MODEL.predict(
        source=pil_image_rgb, 
        device=settings.AI_DEVICE, 
        conf=0.5, # 신뢰도 50% 이상만 '얼굴'로 인정
        verbose=False
    )

    # No faces detected
    if len(results[0].boxes) == 0:
        raise HTTPException(status_code=400, detail="얼굴을 찾을 수 없습니다. 정면 사진을 업로드해주세요.")

    # Crop to the first detected face
    box = results[0].boxes[0]
    (x1, y1, x2, y2) = map(int, box.xyxy[0].cpu().numpy())

    # Center of the face box
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    
    crop_size = settings.IMG_SIZE 
    half_size = crop_size // 2

    left = center_x - half_size
    top = center_y - half_size
    right = center_x + half_size
    bottom = center_y + half_size

    cropped_pil_image = pil_image_rgb.crop((left, top, right, bottom))

    # Center the cropped image on a black canvas if it's smaller than crop_size
    if cropped_pil_image.width != crop_size or cropped_pil_image.height != crop_size:
        final_image = Image.new("RGB", (crop_size, crop_size), (0, 0, 0))
        paste_x = (crop_size - cropped_pil_image.width) // 2
        paste_y = (crop_size - cropped_pil_image.height) // 2
        final_image.paste(cropped_pil_image, (paste_x, paste_y))
        resized_image = final_image
    else:
        resized_image = cropped_pil_image

    # Create directories
    uid = str(uuid.uuid4())
    filename = f"{uid}.jpg"
    original_save_path = settings.STATIC_DIR / user_id / filename
    original_image_url = f"{settings.STATIC_URL_PREFIX}/{user_id}/{filename}"

    original_save_path.parent.mkdir(parents=True, exist_ok=True)
    resized_image.save(original_save_path, format="JPEG", quality=95)
    original_save_path_str = str(original_save_path)
    
    analysis_data = {}

    # LLM Skin Analysis
    description = run_skin_analysis(image_path=original_save_path_str)

    # Wrinkle Analysis
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

    analysis_data.update({
        "wrinkle_score": wrinkle_score,
        "wrinkle_image_url": wrinkle_url,
        "wrinkle_description": description,
    })

    # Acne Analysis
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
    
    analysis_data.update({
        "acne_score": acne_score,
        "acne_image_url": acne_url,
        "acne_description": description,
    })

    # Atopy Analysis
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

    analysis_data.update({
        "atopy_score": atopy_score,
        "atopy_image_url": atopy_url,
        "atopy_description": description,
    })

    # Calculate total score and save to DB
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