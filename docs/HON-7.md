# HON-7: Docker 및 docker-compose 구성

Django 앱과 PostgreSQL 데이터베이스를 Docker 및 docker-compose로 구성하여 로컬 테스트 환경을 쉽게 설정할 수 있도록 합니다.

---

## 기술 스택 추가

| 패키지 | 버전 | 용도 |
|--------|------|------|
| psycopg2-binary | 2.9+ | PostgreSQL 데이터베이스 드라이버 |
| gunicorn | 21+ | WSGI HTTP 서버 |

---

## Docker 구성

| 서비스 | 이미지 | 포트 | 설명 |
|--------|--------|------|------|
| web | Python 3.12 (custom) | 8000 | Django 앱 |
| db | postgres:16-alpine | 5432 | PostgreSQL 데이터베이스 |

---

## Proposed Changes

### Dependencies

#### [MODIFY] [pyproject.toml](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/pyproject.toml)
- `psycopg2-binary>=2.9.9` 의존성 추가
- `gunicorn>=21.0.0` 의존성 추가

---

### Django 설정

#### [MODIFY] [config/settings.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/config/settings.py)
- 환경변수 기반 PostgreSQL 데이터베이스 설정 추가
- `ALLOWED_HOSTS` 환경변수 지원
- `STATIC_ROOT` 설정 추가 (collectstatic 지원)

```python
# 환경변수로 DB 설정 (PostgreSQL/SQLite 자동 전환)
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}
```

---

### Docker Files

#### [NEW] [Dockerfile](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/Dockerfile)
- Python 3.12 slim 베이스 이미지
- uv 패키지 매니저로 의존성 설치
- Gunicorn WSGI 서버 실행

#### [NEW] [docker-compose.yaml](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/docker-compose.yaml)
- `web` 서비스: Django 앱 (Port 8000)
- `db` 서비스: PostgreSQL 16 (Port 5432)
- 볼륨: `postgres_data` (데이터 영속성)

#### [NEW] [.dockerignore](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/.dockerignore)
- `.venv`, `__pycache__`, `.git`, `db.sqlite3` 등 제외

---

### 환경 변수

#### [MODIFY] [.env.example](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/.env.example)
- PostgreSQL 관련 환경변수 추가:
  - `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
  - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (docker-compose용)
  - `ALLOWED_HOSTS`

---

## TODO

- [x] `pyproject.toml`에 psycopg2-binary, gunicorn 추가
- [x] `uv sync` 실행
- [x] `settings.py` PostgreSQL 환경변수 설정 추가
- [x] `Dockerfile` 생성
- [x] `docker-compose.yaml` 생성
- [x] `.dockerignore` 생성
- [x] `.env.example` 업데이트
- [x] Docker 빌드 및 실행 테스트
- [x] 기존 테스트 Docker 환경에서 실행 (pytest는 개발 의존성으로 production 이미지에 미포함)

---

## Verification Plan

### Automated Tests

```bash
# Docker 이미지 빌드
docker build -t market-data-harvester .

# Docker Compose 실행
docker compose up -d

# 마이그레이션 실행
docker compose exec web python manage.py migrate

# 기존 테스트 실행 (20개 테스트)
docker compose exec web python -m pytest apps/

# API 헬스체크
curl http://localhost:8000/api/exchange-rates/
```

### Manual Verification

1. `docker compose up` 으로 컨테이너 시작
2. 브라우저에서 `http://localhost:8000/admin/` 접속 확인
3. API 엔드포인트 `/api/exchange-rates/` 응답 확인
4. `docker compose down -v` 로 정리

---

## 향후 계획

> [!NOTE]
> HON-7 완료 후 고려 사항
> - 운영 환경용 docker-compose.prod.yaml 분리
> - nginx 리버스 프록시 추가
> - Docker Secrets 활용한 비밀 관리
