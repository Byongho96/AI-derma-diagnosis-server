# FastAPI & MySQL Docker
이 프로젝트는 Docker Compose를 사용하여 FastAPI 애플리케이션과 MySQL 데이터베이스를 함께 실행하는 간단한 스타터 템플릿입니다.

## 사전 준비 사항
* Docker
* Docker Compose

## 시작하기
애플리케이션을 실행하려면 아래 단계를 따르세요.


1. 프로젝트의 루트 디렉토리에서 터미널을 열고 아래 명령어를 실행하세요.
    ```bash
    docker-compose up --build
    ```

2. 컨테이너가 성공적으로 실행되면, 웹 브라우저에서 아래 주소로 접속하여 API를 확인할 수 있습니다.
   * API 기본 경로: `http://localhost:8000`
   * Swagger UI (API 문서): `http://localhost:8000/docs`