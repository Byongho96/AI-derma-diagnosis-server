your-project-name/
├── app/
│   ├── api/             # 라우터 (엔드포인트) 정의
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   └── __init__.py
│   ├── core/            # 앱의 공통 설정, 보안 로직, 예외 처리 등 핵심 컴포넌트
│   │   ├── config.py    # 환경 변수, 설정 로드
│   │   ├── security.py  # 비밀번호 해싱, JWT 생성/검증 등 인증 로직
│   │   └── exceptions.py# 커스텀 예외 정의
│   ├── crud/            # CRUD(Create, Read, Update, Delete) 로직 (DB 접근 로직)
│   │   ├── __init__.py
│   │   ├── user.py      # 사용자 관련 DB 쿼리 함수
│   │   └── item.py
│   ├── db/              # 데이터베이스 연결 및 세션 관련
│   │   ├── session.py   # DB 연결 엔진 및 세션 생성
│   │   └── base.py      # ORM 모델의 기본 클래스 (선택 사항)
│   ├── dependencies/    # FastAPI Depends()에 사용될 의존성 주입 함수
│   │   ├── __init__.py
│   │   ├── db.py        # DB 세션 의존성 (get_db)
│   │   └── auth.py      # 현재 사용자 인증 의존성 (get_current_user)
│   ├── models/          # SQLAlchemy/SQLModel 등의 ORM 모델 (DB 스키마)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/         # Pydantic 모델 (API 요청/응답 데이터 유효성 검사 및 직렬화)
│   │   ├── __init__.py
│   │   ├── token.py     # JWT 토큰 스키마
│   │   ├── user.py
│   │   └── item.py
│   └── main.py          # FastAPI 앱 인스턴스 생성 및 라우터 포함 (진입점)
├── tests/               # 테스트 코드 (pytest 등)
├── .env                 # 환경 변수 파일 (DB 접속 정보, Secret Key 등)
├── requirements.txt     # 파이썬 패키지 목록 (pip install -r)
└── Dockerfile           # Docker 배포 시 사용 (선택 사항)