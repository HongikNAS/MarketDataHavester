# Market Data Harvester

환율, 주가, 채권 등 금융 시장 데이터를 수집하고 저장하는 Django 기반 서비스입니다.

## 작업 방법
[!IMPORTANT]
> 아래 규칙은 반드시 준수해야 합니다.

### 1. 계획 (Planning)
- [ ] Plan mode로 Ticket의 이름의 작업 계획서를 작성 (예: docs/HON-5.md)
- [ ] 계획서에 Overview, Proposed Changes, TODO, Verification Plan 포함

### 2. 구현 (Execution)
> [!CAUTION]
> **TODO 단위로 커밋 필수!** 여러  TODO 을 한 번에 커밋하지 않습니다.

- [ ] 각 TODO 완료 시 즉시 커밋
- [ ] 커밋 메시지는 변경사항을 충분히 설명
- [ ] 모든 구현에는 Unit 테스트를 작성

### 3. 검증 (VERIFICATION)
- [ ] 모든 테스트 통과 확인
- [ ] Push 전 최종 점검

## 기술 스택

- **Language**: Python 3.12
- **Framework**: Django 6.x
- **Package Manager**: uv
- **Database**: SQLite (개발), PostgreSQL (운영 예정)

## 프로젝트 구조

```
MarketDataHavester/
├── config/                 # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # Django 앱 모음
│   └── exchange_rates/     # 환율 데이터 수집 앱
├── docs/                   # 문서
│   └── HON-5.md           # 초기 설정 계획서
├── pyproject.toml          # 패키지 및 도구 설정
└── manage.py
```

## 개발 환경 설정

```bash
# 패키지 설치
uv sync

# 개발 의존성 포함 설치
uv sync --dev

# 마이그레이션
uv run python manage.py migrate

# 개발 서버 실행
uv run python manage.py runserver
```

## 환경 변수

`.env` 파일에 다음 변수를 설정:

- `KOREAEXIM_API_KEY`: 한국수출입은행 Open API 인증키

## 앱 설명

### exchange_rates
- 한국수출입은행 Open API를 통한 환율 데이터 수집
- `ExchangeRate` 모델: 통화 코드, 매매기준율, 현찰 매매율 등 저장
- `python manage.py fetch_exchange_rates`: 환율 데이터 수집 커맨드

## 코딩 컨벤션

- **Formatter**: Black (line-length: 120)
- **Linter**: Ruff
- **Import 순서**: isort 규칙 준수
- **테스트**: pytest-django 사용

## 데이터베이스

- 모든 Table에는 created_at, updated_at 컬럼을 포함합니다.
- created_at, updated_at 컬럼은 auto_now_add, auto_now 옵션을 사용합니다.

## 관련 문서

- [docs/HON-5.md](docs/HON-5.md) - 초기 설정 계획서
