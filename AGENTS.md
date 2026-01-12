# Market Data Harvester

환율, 주가, 채권 등 금융 시장 데이터를 수집하고 저장하는 Django 기반 서비스입니다.

## 작업 방법
1. Plan mode로 Ticket 이름으로 작업 계획서를 작성합니다.
2. 작업 계획서는 Overview, Proposed Changes, TODO, Verification Plan 으로 구성하며, Future Work을 포함할 수도 있습니다.
3. Plan mode로 작성된 Ticket 이름으로 Branch를 생성합니다.
4. ToDo 단위로 Commit 을 작성하며, Commit message의 내용은 코드 변경사항을 충분히 설명할 수 있어야 합니다.
5. Verification Plan 은 구현된 내용을 어떻게 Test 할지 작성합니다.
6. 모든 구현에 대하여 Unit 테스트를 작성합니다. 분기될 수 있는 부분에 대해 상세히 Unit 테스트를 작성합니다.
7. 모든 변경사항은 반드시 테스트를 통과한 후에 Push 합니다.

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

## 관련 문서

- [docs/HON-5.md](docs/HON-5.md) - 초기 설정 계획서
