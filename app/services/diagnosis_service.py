import os
import cv2
import numpy as np
import base64
import uuid
import io
import ollama
from ultralytics import YOLO
from fastapi import UploadFile
from sqlalchemy.orm import Session
from PIL import Image, ImageOps
from app.core.config import settings
from pathlib import Path
from datetime import datetime
from app.crud import crud_diagonsis

# 점수 계산: 주름이 이미지의 10% 이상을 차지하면 0점, 0%면 100점
MAX_WRINKLE_RATIO_THRESHOLD = 0.1 
CURRENT_FILE_DIR = Path(__file__).resolve().parent


# --- 1. AI 모델 함수 (제공된 코드 정리) ---
# --- 2. 헬퍼 함수 (점수 계산, 이미지 처리) ---

def calculate_score(masks: np.ndarray) -> int:
    """
    YOLO 마스크 데이터를 기반으로 0-100점 사이의 점수를 계산합니다.
    100점 = 주름 없음 (완벽)
    0점 = 주름이 전체의 (MAX_WRINKLE_RATIO_THRESHOLD * 100)% 이상 차지
    """
    if masks is None or masks.size == 0:
        return 100  # 주름이 감지되지 않으면 100점

    # 모든 마스크를 하나로 합침
    combined_mask = np.any(masks, axis=0)
    
    # 흰색 픽셀(주름) 계산
    white_pixels = np.sum(combined_mask)
    
    # 전체 픽셀 계산 (마스크 크기 기준)
    total_pixels = combined_mask.shape[0] * combined_mask.shape[1]
    if total_pixels == 0:
        return 100 # 이미지가 없는 경우

    # 주름 비율 계산
    ratio = white_pixels / total_pixels

    # 비율을 0-100 점수로 변환 (선형적으로 감소)
    score = 100.0 * (1.0 - (ratio / MAX_WRINKLE_RATIO_THRESHOLD))
    
    # 점수가 0-100 범위를 벗어나지 않도록 클리핑
    return int(np.clip(score, 0, 100))


def run_wrinkle_segmentation(
    img_path: str,
    output_dir: str,
    weight_path: str = f"{CURRENT_FILE_DIR}/weights/wrinkle.pt", # 가중치 경로
    img_size: int = settings.IMG_SIZE,
    device: str = settings.AI_DEVICE
):
    """
    YOLO 모델을 실행하여 주름을 분할하고, 
    결과 오버레이 이미지 경로와 마스크 데이터를 반환합니다.
    """
    if not os.path.exists(weight_path):
        raise FileNotFoundError(f"Weight not found: {weight_path}")
    
    model = YOLO(weight_path)
    results = model.predict(source=img_path, conf=0.25, imgsz=img_size, device=device, save=False, show=False)

    result = results[0]
    if result.masks is None:
        print("No wrinkle masks found.")
        return None, 100

    # 오버레이 이미지 생성 및 저장
    img_rgb = cv2.cvtColor(result.orig_img, cv2.COLOR_BGR2RGB)
    masks = result.masks.data.cpu().numpy()
    combined_mask_viz = np.zeros_like(img_rgb, dtype=np.uint8)

    for mask in masks:
        color = (255, 255, 255) # 마스크를 흰색으로 통일
        combined_mask_viz[mask.astype(bool)] = color

    score = calculate_score(masks)

    overlay = cv2.addWeighted(img_rgb, 0.6, combined_mask_viz, 0.4, 0)
    
    # 결과 저장
    os.makedirs(output_dir, exist_ok=True)
    filename = f"wrinkle_{os.path.basename(img_path)}"
    output_path = os.path.join(output_dir, filename)
    
    overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, overlay_bgr)
    
    return output_path, score


def run_acne_segmentation(
    img_path: str,
    output_dir: str,
    weight_path: str = f"{CURRENT_FILE_DIR}/weights/acne.pt", # 가중치 경로
    img_size: int = settings.IMG_SIZE,
    device: str = settings.AI_DEVICE
):
    """
    YOLO 모델을 실행하여 주름을 분할하고, 
    결과 오버레이 이미지 경로와 마스크 데이터를 반환합니다.
    """
    if not os.path.exists(weight_path):
        raise FileNotFoundError(f"Weight not found: {weight_path}")
    
    model = YOLO(weight_path)
    results = model.predict(source=img_path, conf=0.25, imgsz=img_size, device=device, save=False, show=False)

    result = results[0]
    if result.masks is None:
        print("No acne masks found.")
        return None, 100

    # 오버레이 이미지 생성 및 저장
    img_rgb = cv2.cvtColor(result.orig_img, cv2.COLOR_BGR2RGB)
    masks = result.masks.data.cpu().numpy()
    combined_mask_viz = np.zeros_like(img_rgb, dtype=np.uint8)

    for mask in masks:
        color = (255, 255, 255) # 마스크를 흰색으로 통일
        combined_mask_viz[mask.astype(bool)] = color

    score = calculate_score(masks)

    overlay = cv2.addWeighted(img_rgb, 0.6, combined_mask_viz, 0.4, 0)
    
    # 결과 저장
    os.makedirs(output_dir, exist_ok=True)
    filename = f"acne_{os.path.basename(img_path)}"
    output_path = os.path.join(output_dir, filename)
    
    overlay_bgr = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, overlay_bgr)
    
    return output_path, score


def run_atopy_segmentation(
    img_path: str,
    output_dir: str,
    weight_path: str = f"{CURRENT_FILE_DIR}/weights/atopy.pt", # 가중치 경로
    img_size: int = settings.IMG_SIZE,
    device: str = settings.AI_DEVICE
):
    """
    YOLO 모델을 실행하여 주름을 분할하고, 
    결과 오버레이 이미지 경로와 마스크 데이터를 반환합니다.
    """
    if not os.path.exists(weight_path):
        raise FileNotFoundError(f"Weight not found: {weight_path}")
    
    model = YOLO(weight_path)
    results = model.predict(source=img_path, conf=0.25, imgsz=img_size, device=device, save=False, show=False)

    result = results[0]
    if result.masks is None:
        print("No atopy masks found.")
        return None, 100

    # 오버레이 이미지 생성 및 저장
    img_rgb = cv2.cvtColor(result.orig_img, cv2.COLOR_BGR2RGB)
    masks = result.masks.data.cpu().numpy()
    combined_mask_viz = np.zeros_like(img_rgb, dtype=np.uint8)

    for mask in masks:
        color = (255, 255, 255) # 마스크를 흰색으로 통일
        combined_mask_viz[mask.astype(bool)] = color

    score = calculate_score(masks)
    print("Atopy score:", score)

    overlay = cv2.addWeighted(img_rgb, 0.6, combined_mask_viz, 0.4, 0)
    
    # 결과 저장
    os.makedirs(output_dir, exist_ok=True)
    filename = f"atopy{os.path.basename(img_path)}"
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
    LLaVA와 Gemma 모델을 사용하여 피부 분석 및 한국어 조언을 반환합니다.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    prompt_en = (
        "You are a friendly but professional dermatologist AI.\n"
        "You will be given a close-up image of a user's skin.\n"
        "Do not describe the image.\n"
        f"The main concern is {analysis_type} and talk to the user directly.\n"
        "Give short, natural advice as if speaking to them, in a warm but expert tone.\n"
        "Focus on 1-2 key problems and how to improve them with practical skincare steps.\n"
        "Keep it under 3 short sentences in English."
    )

    res_en = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": prompt_en},
            {
                "role": "user",
                "content": "Look at this skin image and give direct, short advice to the user.",
                "images": [image_base64],
            },
        ],
    )
    english_advice = res_en["message"]["content"].strip()

    prompt_ko = (
        "Translate the following English skincare advice into fluent, natural Korean.\n"
        "Write as if speaking directly to the user.\n"
        "Use only Korean characters (no Japanese, Chinese, or English words).\n"
        "Keep it short (2-3 sentences), polite, and clear.\n"
        "Do not describe the image or add any extra explanation.\n"
        "Text to translate:\n" + english_advice
    )

    res_ko = ollama.chat(
        model=translator_model,
        messages=[
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": prompt_ko},
        ],
    )
    return res_ko["message"]["content"].strip()

def resize_and_save_image(
    contents: bytes, 
    save_path: Path, 
    size: int = settings.IMG_SIZE
) -> None:
    """
    업로드된 이미지(bytes)를 1024x1024로 리사이즈 크롭하여 저장합니다.
    """
    image = Image.open(io.BytesIO(contents))
    
    # ImageOps.fit: 비율 유지하며 자르기 (중앙 기준)
    resized_image = ImageOps.fit(image, (size, size), Image.Resampling.LANCZOS)
    
    # 'static/images' 폴더가 없으면 생성
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # RGBA -> RGB 변환 (JPG 저장 시 필요)
    if resized_image.mode == 'RGBA':
        resized_image = resized_image.convert('RGB')
        
    resized_image.save(save_path, format="JPEG", quality=95)


# --- 3. 메인 서비스 함수 ---

def _run_sync_processing(
    db: Session, 
    contents: bytes, 
    user_id: str
):
    """
    동기적으로 실행되어야 하는 모든 무거운 작업을 처리합니다.
    (FastAPI의 to_thread에서 실행됨)
    """
    
    # 1. 원본 이미지 리사이즈 및 저장
    uid = str(uuid.uuid4())
    filename = f"{uid}.jpg"
    original_save_path = settings.STATIC_DIR / user_id / filename
    original_image_url = f"{ settings.STATIC_URL_PREFIX}/{user_id}/{filename}"

    resize_and_save_image(contents, original_save_path, size=settings.IMG_SIZE)
    
    original_save_path_str = str(original_save_path)

    # 2. 모델 1 (YOLO) 실행 및 점수 계산
    wrinkle_result_dir = str(settings.STATIC_DIR / user_id / uid / "wrinkle")
    
    wrinkle_saved_overlay_path, wrinkle_score = run_wrinkle_segmentation(
        img_path=original_save_path_str,
        output_dir=wrinkle_result_dir,
        device="cpu"
    )
    
    if wrinkle_saved_overlay_path:
        wrinkle_image_url = f"{settings.STATIC_URL_PREFIX}/{user_id}/{uid}/wrinkle/{Path(wrinkle_saved_overlay_path).name}"
    else:
        # 주름이 감지되지 않은 경우: 기본 이미지 사용
        wrinkle_image_url = original_image_url

    # 3. 모델 2 (LLaVA) 실행
    # wrinkle_description = run_skin_analysis(
    #     image_path=original_save_path_str,
    #     analysis_type="wrinkle"
    # )
    wrinkle_description = "주름이 거의 보이지 않습니다. 꾸준한 수분 공급과 자외선 차단제로 피부를 보호하세요."

    # 2. 모델 1 (YOLO) 실행 및 점수 계산
    acne_result_dir = str(settings.STATIC_DIR / user_id / uid / "acne")
    
    acne_saved_overlay_path, acne_score = run_acne_segmentation(
        img_path=original_save_path_str,
        output_dir=acne_result_dir
    )
    
    if acne_saved_overlay_path:
        acne_image_url = f"{settings.STATIC_URL_PREFIX}/{user_id}/{uid}/acne/{Path(acne_saved_overlay_path).name}"
    else:
        # 주름이 감지되지 않은 경우: 기본 이미지 사용
        acne_image_url = original_image_url

    # 3. 모델 2 (LLaVA) 실행
    # acne_description = run_skin_analysis(
    #     image_path=original_save_path_str,
    #     analysis_type="acne",
    #     device="cpu"
    # )
    acne_description = "여드름이 거의 보이지 않습니다. 규칙적인 세안과 비자극성 보습제를 사용하세요."

        # 2. 모델 1 (YOLO) 실행 및 점수 계산
    atopy_result_dir = str(settings.STATIC_DIR / user_id / uid / "atopy")
    
    atopy_saved_overlay_path, atopy_score = run_atopy_segmentation(
        img_path=original_save_path_str,
        output_dir=atopy_result_dir
    )
    
    if atopy_saved_overlay_path:
        atopy_image_url = f"{settings.STATIC_URL_PREFIX}/{user_id}/{uid}/atopy/{Path(atopy_saved_overlay_path).name}"
    else:
        # 주름이 감지되지 않은 경우: 기본 이미지 사용
        atopy_image_url = original_image_url

    # 3. 모델 2 (LLaVA) 실행
    # atopy_description = run_skin_analysis(
    #     image_path=original_save_path_str,
    #     analysis_type="atopy"
    # )
    atopy_description = "아토피 증상이 거의 보이지 않습니다. 자극적인 성분을 피하고, 보습을 철저히 하세요."

    # 4. DB 저장을 위한 스키마 준비
    # TODO: total_score가 wscore 외에 다른 점수와 합산되어야 한다면 로직 수정 필요
    total_score = (wrinkle_score + acne_score + atopy_score) // 3

    now_kst = datetime.now()
    created_at = now_kst.strftime("%Y-%m-%dT%H:%M:%S")
    
    # 5. DB에 저장 (CRUD 함수 호출)
    db_diagnosis = crud_diagonsis.create_diagnosis(
            db=db,
            user_id=user_id,
            original_image_url=original_image_url,
            created_at=created_at,
            total_score=total_score,
            wrinkle_score=wrinkle_score,
            wrinkle_image_url=wrinkle_image_url,
            wrinkle_description=wrinkle_description,
            acne_score=acne_score,
            acne_image_url=acne_image_url,
            acne_description=acne_description,
            atopy_score=atopy_score,
            atopy_image_url=atopy_image_url,
            atopy_description=atopy_description
        )
    return db_diagnosis


async def process_diagnosis(
    db: Session, 
    file: UploadFile, 
    user_id: str
):
    """
    비동기 엔드포인트에서 호출되는 메인 서비스 함수입니다.
    파일 읽기는 비동기로, 무거운 처리는 동기 함수로 분리하여 실행합니다.
    """
    # 1. (비동기) 파일 내용 읽기
    contents = await file.read()
    
    # 2. (동기) 모든 CPU/GPU 바운드 작업을 별도 스레드에서 실행
    # (FastAPI 이벤트 루프를 막지 않기 위함)
    
    # loop = asyncio.get_event_loop()
    # db_diagnosis = await loop.run_in_executor(
    #     None, _run_sync_processing, db, contents, user_id
    # )
    
    # 참고: Python 3.9+ 에서는 asyncio.to_thread 사용
    import asyncio
    db_diagnosis = await asyncio.to_thread(
        _run_sync_processing, db, contents, user_id
    )

    # (간결성을 위해, 동기 함수를 그대로 호출합니다. 
    #  실제 프로덕션에서는 위 주석의 run_in_executor 또는 to_thread 사용을 권장합니다.)
    # db_diagnosis = _run_sync_processing(db, contents, user_id)

    return db_diagnosis