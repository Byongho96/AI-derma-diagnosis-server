# AI 피부 진단 서버 운영 가이드

## 목차
1. [시스템 개요](#시스템-개요)
2. [시스템 구조](#시스템-구조)
3. [환경 설정](#환경-설정)
4. [서버 실행 방법](#서버-실행-방법)
5. [서버 종료 방법](#서버-종료-방법)
6. [상태 확인 및 모니터링](#상태-확인-및-모니터링)
7. [문제 해결](#문제-해결)
8. [백업 및 복원](#백업-및-복원)

---

## 시스템 개요

### 제품 소개
AI 피부 진단 서버는 사용자가 업로드한 피부 사진을 분석하여 다음 세 가지 피부 상태를 진단하는 웹 서버입니다:

- **여드름 (Acne)** 진단
- **아토피 (Atopy)** 진단  
- **주름 (Wrinkle)** 진단

진단 결과를 바탕으로 AI가 개인 맞춤형 피부 관리 조언을 제공합니다.

### 주요 기능
- 피부 사진 업로드 및 AI 진단
- 진단 결과 데이터베이스 저장
- 사용자 계정 관리 및 인증
- 진단 히스토리 조회
- AI 기반 맞춤형 피부 관리 조언 제공
- REST API 형태로 모바일 앱, 웹사이트 연동 가능

---

## 시스템 구조

### 전체 아키텍처
시스템은 3개의 독립적인 서비스로 구성되어 있으며, Docker를 통해 관리됩니다:

```
┌────────────────────────────────────────────────────────────────────┐
│                  AI 피부 진단 서버 (FastAPI)                         │
│                                                                    │
│  • 포트: 8000                                                       │ 
│  • 역할: API 서버, 이미지 처리, AI 진단                               │
│  • 기술: Python, FastAPI, PyTorch, YOLO                            │
│  • 데이터: 사용자 정보, 진단 결과, 파일 업로드                          │
└────────────────────────────────────────────────────────────────────┘
                    ↓                            ↓
┌────────────────────────────────┐    ┌──────────────────────────────────┐
│        데이터베이스 (MySQL)      │    │        AI 언어모델 (Ollama)       │
│                                │    │                                  │
│  • 포트: 3306                   │    │  • 포트: 11434                   │
│  • 역할: 데이터 저장              │    │  • 역할: 맞춤형 조언 생성          │
│  • 저장 데이터:                  │    │  • 모델: llava, gemma2:9b        │
│    - 사용자 계정                 │    │  • 기능: 이미지 이해, 텍스트 생성   │
│    - 진단 결과                  │    │                                  │
│    - 진단 히스토리               │    │                                  │
└──────────────── ───────────────┘    └──────────────────────────────────┘
```

### 데이터 흐름
1. **사용자 요청** → 피부 사진을 API 서버로 업로드
2. **AI 진단** → YOLO 모델이 피부 상태 분석 (여드름, 아토피, 주름)
3. **데이터 저장** → 진단 결과를 MySQL 데이터베이스에 저장
4. **AI 조언 생성** → Ollama LLM이 개인 맞춤형 피부 관리 조언 생성
5. **결과 반환** → 진단 결과와 조언을 사용자에게 전달

---

## 환경 설정

### 시스템 요구사항

#### 최소 사양
- **운영체제**: Windows 10/11, macOS, Linux
- **CPU**: 4코어 이상
- **메모리**: 24GB 이상
- **저장공간**: 20GB 이상 여유공간
- **네트워크**: 인터넷 연결 (최초 설치 시 AI 모델 다운로드)

#### 권장 사양
- **CPU**: 8코어 이상
- **메모리**: 32GB 이상  
- **저장공간**: 50GB 이상
- **GPU**: NVIDIA GPU (선택사항, AI 처리 속도 향상)

### 필수 소프트웨어 설치

#### 1. Docker 설치
**Windows:**
1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드
2. 설치 파일 실행 후 안내에 따라 설치
3. 설치 완료 후 재부팅

**macOS:**
1. [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) 다운로드
2. .dmg 파일을 열어 Applications 폴더로 드래그

**Linux (Ubuntu):**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 2. 설치 확인
터미널(명령 프롬프트)에서 다음 명령어로 설치 확인:
```bash
docker --version
docker-compose --version
```

### 환경 변수 설정

프로젝트 폴더 내에 `.env` 파일이 있습니다. 이 파일의 각 설정값을 설명드리겠습니다:

#### 데이터베이스 설정 (필수 수정)
```env
# MySQL 루트 사용자 비밀번호 (강력한 비밀번호로 변경 필요)
MYSQL_ROOT_PASSWORD=mysecretrootpassword

# 생성할 데이터베이스 이름 (원하는 이름으로 변경 가능)
MYSQL_DATABASE=mydatabase

# 애플리케이션에서 사용할 MySQL 사용자명 (원하는 이름으로 변경 가능)
MYSQL_USER=user

# 애플리케이션 사용자 비밀번호 (강력한 비밀번호로 변경 필요)
MYSQL_PASSWORD=password
```

**⚠️ 보안 주의사항:**
- `MYSQL_ROOT_PASSWORD`와 `MYSQL_PASSWORD`는 반드시 강력한 비밀번호로 변경하세요
- 비밀번호는 최소 12자 이상, 영문 대소문자, 숫자, 특수문자 조합 권장

#### 애플리케이션 보안 설정 (필수 수정)
```env
# JWT 토큰 암호화 알고리즘 (변경하지 마세요)
ALGORITHM=HS256

# JWT 토큰 서명에 사용되는 비밀키 (반드시 변경 필요)
SECRET_KEY=my_super_secret_key_from_root_env
```

**⚠️ 보안 주의사항:**
- `SECRET_KEY`는 반드시 복잡하고 긴 문자열로 변경하세요
- 추천: 최소 32자 이상의 랜덤 문자열

#### AI 처리 설정
```env
# AI 모델이 사용할 디바이스 설정
AI_DEVICE=cpu
# 옵션: cpu (CPU 사용) 또는 cuda (NVIDIA GPU 사용)
```

**설정 가이드:**
- **cpu**: 일반적인 경우, 안정적이지만 처리 속도가 느림
- **cuda**: NVIDIA GPU가 있는 경우, 빠른 처리 속도

#### 이메일 서비스 설정 (선택사항)
```env
# Gmail 또는 기업 이메일 계정 설정 (비밀번호 재설정 등에 사용)
# MAIL_USERNAME=your_email@gmail.com
# MAIL_PASSWORD=your_app_password  
# MAIL_FROM=your_email@gmail.com
# MAIL_FROM_NAME=AI 피부 진단 서비스
```

**설정방법 (Gmail 예시):**
1. Gmail 2단계 인증 활성화
2. 앱 비밀번호 생성
3. 위 설정값의 주석(#) 제거 후 실제 값 입력

---

## 서버 실행 방법

### 1. 기본 실행 (백그라운드)

가장 일반적인 실행 방법입니다. 서버가 백그라운드에서 실행되어 터미널을 닫아도 계속 동작합니다.

```bash
# 프로젝트 폴더로 이동
cd /path/to/AI-derma-diagnosis-server

# 백그라운드에서 모든 서비스 실행
docker-compose up -d
```

### 2. 로그 확인하며 실행

최초 실행 시 또는 문제 해결 시 사용합니다. AI 모델 다운로드 진행상황을 실시간으로 확인할 수 있습니다.

```bash
# 로그를 화면에 표시하며 실행
docker-compose up
```

**최초 실행 시 예상 시간:**
- 데이터베이스 초기화: 1-2분
- AI 모델 다운로드 (llava, gemma2:9b): 10-30분 (인터넷 속도에 따라)
- 전체 서비스 준비: 15-35분

### 3. 특정 서비스만 실행

```bash
# FastAPI 서버만 실행
docker-compose up app

# 데이터베이스만 실행  
docker-compose up db

# AI 모델 서버만 실행
docker-compose up ollama_server
```

### 4. 실행 상태 확인

```bash
# 실행 중인 서비스 확인
docker-compose ps

# 모든 서비스가 정상적으로 실행 중인 경우 출력 예시:
#      Name                     Command               State           Ports
# --------------------------------------------------------------------------------
# fastapi_server    /app/entrypoint.sh              Up      0.0.0.0:8000->8000/tcp
# mysql_db          docker-entrypoint.sh mysqld     Up      0.0.0.0:3306->3306/tcp  
# ollama_server     /bin/sh -c echo 'Starting...    Up      0.0.0.0:11434->11434/tcp
```

### 5. 서비스 접속 확인

서버가 정상 실행되면 웹브라우저에서 다음 주소로 접속 가능합니다:

- **API 문서**: http://localhost:8000/docs
- **API 상태 확인**: http://localhost:8000/
- **대체 API 문서**: http://localhost:8000/redoc

---

## 서버 종료 방법

### 1. 일반 종료 (데이터 보존)

일시적으로 서버를 중단하지만 데이터베이스 내용과 다운로드한 AI 모델은 보존됩니다.

```bash
# 모든 서비스 중지 (데이터 보존)
docker-compose down
```

이 방법으로 종료 후 다시 `docker-compose up -d`로 실행하면 기존 데이터가 그대로 유지됩니다.

### 2. 완전 종료 (데이터 삭제)

**⚠️ 주의: 이 방법은 모든 데이터를 삭제합니다**

```bash
# 서비스 중지 + 데이터베이스 삭제 + AI 모델 삭제
docker-compose down -v
```

**삭제되는 데이터:**
- 모든 사용자 계정 정보
- 모든 진단 결과 및 히스토리  
- 다운로드한 AI 모델 (llava, gemma2:9b)

### 3. 시스템 정리 종료

서버를 완전히 제거하고 디스크 공간을 확보하려는 경우:

```bash
# 서비스 중지 + 모든 데이터 삭제 + Docker 이미지 삭제
docker-compose down -v --rmi all
```

### 4. 긴급 종료

서버가 응답하지 않을 때:

```bash
# 강제로 모든 컨테이너 중지
docker-compose kill

# 그 후 정리
docker-compose down
```

---

## 상태 확인 및 모니터링

### 1. 전체 서비스 상태 확인

```bash
# 실행 중인 모든 서비스 상태 보기
docker-compose ps

# 서비스 상태 상세 정보
docker-compose top
```

### 2. 개별 서비스 로그 확인

```bash
# FastAPI 서버 로그 (실시간)
docker-compose logs -f app

# 데이터베이스 로그 (실시간)  
docker-compose logs -f db

# AI 모델 서버 로그 (실시간)
docker-compose logs -f ollama_server

# 모든 서비스 로그 (실시간)
docker-compose logs -f
```

### 3. 서비스 접속 테스트

```bash
# API 서버 응답 테스트
curl http://localhost:8000/

# 데이터베이스 연결 테스트 (컨테이너 내부에서)
docker-compose exec db mysql -u user -p mydatabase

# AI 모델 서버 상태 테스트
curl http://localhost:11434/api/tags
```

### 4. 리소스 사용량 모니터링

```bash
# 컨테이너별 CPU, 메모리 사용량 실시간 모니터링
docker stats

# 디스크 사용량 확인
docker system df
```

### 5. 건강 상태 확인

시스템에 내장된 헬스 체크 기능으로 각 서비스의 상태를 자동 확인합니다:

- **데이터베이스**: MySQL 연결 상태 자동 체크
- **AI 모델 서버**: llava, gemma2:9b 모델 로딩 상태 자동 체크
- **API 서버**: 데이터베이스 및 AI 서버 의존성 체크

---

## 문제 해결

### 1. 서버가 시작되지 않는 경우

**증상**: `docker-compose up` 실행 시 오류 발생

**해결 방법**:
```bash
# 1. 이전 컨테이너 완전 정리
docker-compose down -v

# 2. Docker 이미지 새로 빌드
docker-compose build --no-cache

# 3. 다시 실행
docker-compose up -d
```

### 2. 포트 충돌 오류

**증상**: "포트가 이미 사용 중" 오류 메시지

**해결 방법**:
```bash
# 포트 사용 프로세스 확인
# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :3306

# macOS/Linux:
lsof -i :8000
lsof -i :3306

# 해당 프로세스 종료 후 다시 실행
```

### 3. AI 모델 다운로드 실패

**증상**: Ollama 서버가 계속 재시작되거나 모델을 찾을 수 없음

**해결 방법**:
```bash
# 1. Ollama 컨테이너 로그 확인
docker-compose logs ollama_server

# 2. 수동으로 모델 다운로드
docker-compose exec ollama_server ollama pull llava
docker-compose exec ollama_server ollama pull gemma2:9b

# 3. 서비스 재시작
docker-compose restart ollama_server
```

### 4. 데이터베이스 연결 오류

**증상**: FastAPI 서버에서 데이터베이스 연결 실패

**해결 방법**:
```bash
# 1. .env 파일의 데이터베이스 설정 확인
cat .env

# 2. MySQL 컨테이너 상태 확인
docker-compose exec db mysql -u root -p

# 3. 연결 테스트
docker-compose exec app python -c "
from app.db.session import engine
print('Database connection:', engine.connect())
"
```

### 5. 메모리 부족 오류

**증상**: 컨테이너가 갑자기 종료되거나 "Out of Memory" 오류

**해결 방법**:
```bash
# 1. 시스템 메모리 사용량 확인
docker stats

# 2. AI_DEVICE를 cpu로 변경 (.env 파일)
AI_DEVICE=cpu

# 3. Docker 메모리 제한 증가 (Docker Desktop 설정)
# Docker Desktop > Settings > Resources > Memory 증가
```

### 6. 권한 오류 (Linux/macOS)

**증상**: Permission denied 오류

**해결 방법**:
```bash
# Docker 권한 추가
sudo usermod -aG docker $USER

# 로그아웃 후 다시 로그인, 또는
newgrp docker

# 파일 권한 확인
ls -la .env
chmod 644 .env
```

---

## 백업 및 복원

### 1. 데이터베이스 백업

```bash
# 데이터베이스 전체 백업
docker-compose exec db mysqldump -u root -p mydatabase > backup_$(date +%Y%m%d_%H%M%S).sql

# 특정 테이블만 백업
docker-compose exec db mysqldump -u root -p mydatabase users diagnoses > backup_essential.sql
```

### 2. 데이터베이스 복원

```bash
# 백업 파일에서 복원
docker-compose exec -T db mysql -u root -p mydatabase < backup_20231121_143000.sql
```

### 3. 전체 시스템 백업

```bash
# 1. 서비스 중지
docker-compose down

# 2. 볼륨 데이터 백업
docker run --rm -v ai-derma-diagnosis-server_db_data:/data -v $(pwd):/backup alpine tar czf /backup/db_backup.tar.gz -C /data .
docker run --rm -v ai-derma-diagnosis-server_ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama_backup.tar.gz -C /data .

# 3. 설정 파일 백업
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup
```

### 4. 전체 시스템 복원

```bash
# 1. 볼륨 생성
docker volume create ai-derma-diagnosis-server_db_data
docker volume create ai-derma-diagnosis-server_ollama_data

# 2. 백업 데이터 복원
docker run --rm -v ai-derma-diagnosis-server_db_data:/data -v $(pwd):/backup alpine tar xzf /backup/db_backup.tar.gz -C /data
docker run --rm -v ai-derma-diagnosis-server_ollama_data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama_backup.tar.gz -C /data

# 3. 설정 파일 복원
cp .env.backup .env
cp docker-compose.yml.backup docker-compose.yml

# 4. 서비스 시작
docker-compose up -d
```

---

## 추가 정보

### 성능 최적화

**GPU 사용 활성화** (NVIDIA GPU가 있는 경우):
1. NVIDIA Container Toolkit 설치
2. `.env` 파일에서 `AI_DEVICE=cuda`로 변경
3. `docker-compose.yml`에서 GPU 설정 주석 해제

**메모리 최적화**:
- 시스템 메모리가 부족한 경우 Docker Desktop의 메모리 할당량 조정
- 불필요한 다른 프로그램 종료


---

**⚠️ 중요한 보안 권고사항**
- `.env` 파일의 비밀번호들은 반드시 강력한 비밀번호로 변경하세요
- 서버를 인터넷에 직접 노출하지 마시고, 방화벽이나 VPN을 통해 보호하세요
- 정기적으로 데이터베이스 백업을 수행하세요
- 시스템 업데이트가 있을 때는 개발팀의 안내에 따라 진행하세요
