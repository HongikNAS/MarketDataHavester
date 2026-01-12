# Market Data Harvester - 초기 설정 계획서

환율, 주가, 채권 정보를 수집하는 Django 기반 서비스의 초기 설정 계획입니다.
**1차 목표**: 환율 데이터 수집 기능 구현

---

## 기술 스택

| 구분 | 선택 | 버전 |
|------|------|------|
| Language | Python | 3.12 |
| Framework | Django | 6.x |
| Package Manager | uv | latest |
| Database | SQLite (개발) → PostgreSQL (운영) | - |
| Task Queue | Celery + Redis (향후) | - |
| API Client | requests | 2.31+ |

---

## 환율 API 정보

> [!IMPORTANT]
> 한국수출입은행 Open API 사용 예정
> - **URL**: `https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON`
> - **인증**: API 키 필요 (수출입은행 홈페이지에서 발급)
> - **호출 제한**: 일 1,000회
> - **응답 형식**: JSON

---

## 프로젝트 구조

```
MarketDataHavester/
├── pyproject.toml          # uv 패키지 설정
├── .python-version         # Python 3.12
├── .env                    # 환경 변수 (API 키 등)
├── .env.example            # 환경 변수 예시
├── manage.py
├── config/                 # Django 설정
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── apps/
    └── exchange_rates/     # 환율 앱
        ├── __init__.py
        ├── models.py       # ExchangeRate 모델
        ├── admin.py
        ├── services.py     # API 호출 로직
        └── management/
            └── commands/
                └── fetch_exchange_rates.py  # 수동 수집 커맨드
```

---

## Proposed Changes

### Core Setup

#### [MODIFY] [pyproject.toml](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/pyproject.toml)
- Python 버전을 `3.12`로 고정
- Django 6.x 및 필수 패키지 추가
- 개발 도구 (pytest, ruff, black) 설정

#### [NEW] [.python-version](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/.python-version)
- Python 3.12 버전 명시

#### [NEW] [.env.example](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/.env.example)
- 환경 변수 템플릿 (API 키 등)

---

### Django Configuration

#### [NEW] [config/settings.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/config/settings.py)
- Django 프로젝트 설정
- 환경 변수 로딩 (python-dotenv)
- 앱 등록, 데이터베이스 설정

#### [NEW] [config/urls.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/config/urls.py)
- URL 라우팅 설정

#### [NEW] [manage.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/manage.py)
- Django 관리 스크립트

---

### Exchange Rates App

#### [NEW] [apps/exchange_rates/models.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/apps/exchange_rates/models.py)
환율 데이터 모델:
```python
class ExchangeRate(models.Model):
    code = models.CharField(max_length=10)             # USD, EUR, JPY 등
    name = models.CharField(max_length=50)             # 미국 달러, 유로 등
    base_rate = models.DecimalField(...)               # 매매기준율
    cash_buy_rate = models.DecimalField(...)           # 현찰 살 때
    cash_sell_rate = models.DecimalField(...)          # 현찰 팔 때
    date = models.DateField()                          # 고시일
    fetched_at = models.DateTimeField(auto_now_add=True)
```

#### [NEW] [apps/exchange_rates/services.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/apps/exchange_rates/services.py)
- 수출입은행 API 호출 로직
- 응답 파싱 및 DB 저장

#### [NEW] [apps/exchange_rates/management/commands/fetch_exchange_rates.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/apps/exchange_rates/management/commands/fetch_exchange_rates.py)
- `python manage.py fetch_exchange_rates` 커맨드

---

## TODO

### Core Setup
- [x] `pyproject.toml` - Python 3.12 및 Django 6.x 패키지 설정
- [x] `.python-version` - Python 3.12 버전 고정
- [x] `.env.example` - 환경 변수 템플릿 생성
- [x] `uv sync` - 패키지 설치 완료 (Django 6.0.1)

### Django Configuration
- [x] `config/__init__.py` - 패키지 초기화
- [x] `config/settings.py` - Django 설정 (한국어/서울 시간대)
- [x] `config/urls.py` - URL 라우팅
- [x] `config/wsgi.py` - WSGI 설정
- [x] `manage.py` - Django 관리 스크립트

### Exchange Rates App
- [x] `apps/exchange_rates/__init__.py` - 앱 패키지 초기화
- [x] `apps/exchange_rates/apps.py` - 앱 설정
- [x] `apps/exchange_rates/models.py` - ExchangeRate 모델
- [x] `apps/exchange_rates/admin.py` - Admin 설정
- [x] `apps/exchange_rates/services.py` - API 호출 서비스
- [x] `apps/exchange_rates/management/commands/fetch_exchange_rates.py` - 수집 커맨드

### Verification
- [x] `uv run python manage.py check` - 시스템 체크 통과
- [x] `uv run python manage.py makemigrations` - 마이그레이션 생성
- [x] `uv run python manage.py migrate` - 마이그레이션 적용

---

## Verification Plan

### Automated Tests
```bash
# 패키지 설치 확인
uv sync

# Django 프로젝트 체크
uv run python manage.py check

# 마이그레이션 생성 및 적용
uv run python manage.py makemigrations
uv run python manage.py migrate

# 개발 서버 실행 테스트
uv run python manage.py runserver
```

### Manual Verification
1. 수출입은행 API 키 발급 후 `.env` 파일에 설정
2. `python manage.py fetch_exchange_rates` 실행하여 데이터 수집 확인
3. Django Admin에서 수집된 환율 데이터 확인

---

## 향후 확장 계획

> [!NOTE]
> 1차 구현 후 추가 예정
> - **REST API 엔드포인트 (DRF)** - n8n/dkron 외부 호출용
> - Celery를 이용한 자동 스케줄링 (매일 특정 시간 수집)
> - 주가 데이터 수집 앱 추가
> - 채권 데이터 수집 앱 추가
