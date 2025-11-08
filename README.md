# AI 피부 진단 서버

## 프로젝트 개요

AI 서비스 기반의 피부 진단 서버 API입니다. 사용자가 업로드한 피부 사진을 분석하여 다음 피부 상태를 진단합니다:

YOLO 모델을 활용하여 **여드름 (Acne)**, **아토피 (Atopy)**, **주름 (Wrinkle)** 진단을 수행하고, 진단 결과를 바탕으로 **Ollama 기반 LLM 모델**(llava, gemma2:9b)을 활용하여 사용자에게 맞춤형 피부 관리 지침을 제공합니다.

## 기술 스택

- **FastAPI**: 고성능 Python 웹 프레임워크
- **PyTorch + Ultralytics YOLO**: AI 기반 이미지 세그멘테이션
- **MySQL**: 사용자 및 진단 데이터 저장
- **Ollama**: 로컬 LLM 서버 (llava, gemma2:9b 모델)
- **Docker Compose**: 멀티 컨테이너 오케스트레이션

## 프로젝트 구조

Docker Compose를 통해 다음 3개의 서비스가 연동됩니다:

```
┌───────────────────────────────────────────────────┐
│  FastAPI 서버 (app)                                │
│  - 포트: 8000                                      │
│  - 역할: REST API 제공, AI 진단 처리                 │
│  - 의존성: MySQL, Ollama                           │
└───────────────────────────────────────────────────┘
             ↓                 ↓
┌──────────────────────┐  ┌────────────────────────┐
│  MySQL (db)          │  │  Ollama (ollama_server)│
│  - 포트: 3306         │  │  - 포트: 11434         │
│  - 역할: 데이터베이스   │  │  - 역할: LLM 추론       │
└──────────────────────┘  └────────────────────────┘
```

## 사용 방법

### 사전 준비

프로젝트 루트에 `.env` 파일을 생성하고 다음 환경 변수를 편집합니다:

```env
# MySQL 설정
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=skin_diagnosis_db
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# JWT 설정
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
```

### 1. Docker Compose 시작

전체 서비스를 백그라운드에서 실행:

```bash
docker-compose up -d
```

로그를 확인하며 실행 (Ollama 모델 다운로드 진행 상황 확인):

```bash
docker-compose up
```

### 2. 서비스 상태 확인

실행 중인 컨테이너 확인:

```bash
docker-compose ps
```

특정 서비스의 로그 확인:

```bash
# FastAPI 서버 로그
docker-compose logs -f app

# Ollama 서버 로그
docker-compose logs -f ollama_server

# MySQL 로그
docker-compose logs -f db
```

### 3. API 접속

FastAPI 서버가 정상적으로 실행되면 다음 URL로 접속 가능합니다:

- API 문서 (Swagger UI): http://localhost:8000/docs
- Alternative API 문서 (ReDoc): http://localhost:8000/redoc
- Health Check: http://localhost:8000/

### 4. Docker Compose 업데이트

코드 변경 후 서비스 재빌드 및 재시작:

```bash
# 전체 서비스 재빌드
docker-compose up -d --build

# 특정 서비스만 재빌드
docker-compose up -d --build app
```

이미지 및 컨테이너 정리 후 재시작:

```bash
docker-compose down
docker-compose up -d --build
```

### 5. Docker Compose 종료

#### 컨테이너만 종료 (볼륨 유지)

데이터베이스 데이터 및 Ollama 모델을 보존합니다:

```bash
docker-compose down
```

#### 컨테이너 + 볼륨 삭제 (완전 초기화)

**주의**: 데이터베이스의 모든 데이터와 다운로드한 LLM 모델이 삭제됩니다:

```bash
docker-compose down -v
```

#### 컨테이너 + 이미지 삭제

빌드된 이미지까지 제거:

```bash
docker-compose down --rmi all
```

#### 완전 정리 (컨테이너 + 볼륨 + 이미지)

```bash
docker-compose down -v --rmi all
```

## 필요 환경

### 시스템 요구사항

| 항목 | 최소 사양 | 권장 사양 |
|------|-----------|-----------|
| **OS** | Linux / Windows / macOS | Ubuntu 22.04 LTS |
| **CPU** | 4 cores | 8 cores 이상 |
| **RAM** | 8GB | 16GB 이상 |
| **디스크 공간** | 20GB | 50GB 이상 (모델 저장 공간 포함) |

### GPU 요구사항 (선택사항)

LLM 추론 속도 향상을 위해 GPU 사용을 권장합니다:

- **GPU**: NVIDIA GPU (CUDA 지원)
- **VRAM**: 8GB 이상 권장 (gemma2:9b 모델 기준)
- **CUDA**: 11.8 이상
- **NVIDIA Container Toolkit**: Docker에서 GPU를 사용하기 위해 필요

#### GPU 비활성화 방법

GPU가 없는 환경에서는 `docker-compose.yml`의 다음 섹션을 주석 처리하세요:

```yaml
# 주석 처리할 부분
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: 1 
#           capabilities: [gpu]
```

### 주요 소프트웨어 버전

- **Docker**: 24.0 이상
- **Docker Compose**: 2.20 이상
- **Python**: 3.11 (FastAPI 컨테이너 내부)
- **MySQL**: 8.0
- **PyTorch**: 2.9.0
- **Ultralytics YOLO**: 8.3.225
- **FastAPI**: 0.121.0

### 필수 Python 패키지

주요 의존성은 `requirements.txt`에 명시되어 있습니다:

```
fastapi==0.121.0
uvicorn==0.38.0
sqlalchemy==2.0.44
pymysql==1.1.2
torch==2.9.0
torchvision==0.24.0
ultralytics==8.3.225
httpx==0.28.1
pillow==12.0.0
opencv-python-headless
pydantic==2.12.4
pydantic-settings==2.11.0
PyJWT==2.10.1
python-multipart==0.0.20
python-dotenv==1.2.1
```