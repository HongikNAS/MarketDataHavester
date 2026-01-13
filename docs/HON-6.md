# HON-6: MarketDataHarvester DRF 구현

환율 데이터를 CLI가 아닌 **REST API 호출**을 통해 접근할 수 있도록 Django REST Framework를 구현합니다.

---

## 기술 스택 추가

| 패키지 | 버전 | 용도 |
|--------|------|------|
| djangorestframework | 3.15+ | REST API 프레임워크 |

---

## API 엔드포인트 설계

| Method | Endpoint | 설명 |
|--------|----------|------|
| `GET` | `/api/exchange-rates/` | 환율 목록 조회 (필터링/페이지네이션) |
| `GET` | `/api/exchange-rates/{code}/` | 특정 통화의 전체 환율 이력 |
| `GET` | `/api/exchange-rates/{code}/dates/{date}/` | 특정 통화의 특정 날짜 환율 |
| `POST` | `/api/exchange-rates/fetch/` | 오늘 날짜 환율 수집 |
| `POST` | `/api/exchange-rates/fetch/dates/{date}/` | 특정 날짜 환율 수집 |

### 필터링 파라미터 (목록 조회)
- `code`: 통화 코드 (USD, EUR, JPY 등)
- `date`: 고시일 (YYYY-MM-DD)
- `date_from`, `date_to`: 날짜 범위

### 응답 예시
```json
{
  "count": 25,
  "next": "/api/exchange-rates/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "USD",
      "name": "미국 달러",
      "base_rate": "1432.50",
      "cash_buy_rate": "1460.00",
      "cash_sell_rate": "1405.00",
      "remit_send_rate": "1447.00",
      "remit_receive_rate": "1418.00",
      "date": "2026-01-13",
      "fetched_at": "2026-01-13T07:00:00Z"
    }
  ]
}
```

---

## Proposed Changes

### Dependencies

#### [MODIFY] [pyproject.toml](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/pyproject.toml)
- `djangorestframework>=3.15.0` 의존성 추가

---

### DRF 설정

#### [MODIFY] [config/settings.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/config/settings.py)
- `INSTALLED_APPS`에 `rest_framework` 추가
- REST_FRAMEWORK 설정 (페이지네이션, 인증 등)

---

### API 구현

#### [NEW] [apps/exchange_rates/serializers.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/apps/exchange_rates/serializers.py)
```python
class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = '__all__'
```

#### [NEW] [apps/exchange_rates/views.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/apps/exchange_rates/views.py)
- `ExchangeRateViewSet`: 환율 목록/필터링
- `by_code`: 통화 코드별 조회 (`/api/exchange-rates/{code}/`)
- `by_code_and_date`: 통화+날짜 조회 (`/api/exchange-rates/{code}/dates/{date}/`)
- `fetch`: 환율 수집 트리거 (`/api/exchange-rates/fetch/`, `/api/exchange-rates/fetch/dates/{date}/`)

#### [NEW] [apps/exchange_rates/urls.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/apps/exchange_rates/urls.py)
- Router를 이용한 ViewSet URL 등록

#### [MODIFY] [config/urls.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/config/urls.py)
- `/api/` 경로로 exchange_rates 앱 URL 연결

---

### 테스트

#### [MODIFY] [apps/exchange_rates/tests.py](file:///home/wonjaek36/workspace/HongikNAS/MarketDataHavester/apps/exchange_rates/tests.py)
- API 엔드포인트 테스트 케이스 추가:
  - 환율 목록 조회
  - 필터링 (code, date)
  - 상세 조회
  - fetch 액션 트리거

---

## TODO

- [x] `pyproject.toml`에 DRF 추가
- [x] `uv sync` 실행
- [x] `settings.py`에 DRF 설정
- [x] `serializers.py` 생성
- [x] `views.py` 생성 (ViewSet)
- [x] `urls.py` 생성 (Router)
- [x] `config/urls.py` 수정
- [x] API 테스트 케이스 작성
- [x] 전체 테스트 실행 (20개 통과)

---

## Verification Plan

### Automated Tests

```bash
# 전체 테스트 실행
uv run python manage.py test apps.exchange_rates

# 또는 pytest 사용
uv run pytest apps/exchange_rates/
```

### Manual Verification

1. 개발 서버 실행:
```bash
uv run python manage.py runserver
```

2. API 테스트 (curl 또는 브라우저):
```bash
# 환율 목록 조회
curl http://localhost:8000/api/exchange-rates/

# USD 전체 이력 조회
curl http://localhost:8000/api/exchange-rates/USD/

# USD 특정 날짜 조회
curl http://localhost:8000/api/exchange-rates/USD/dates/2026-01-13/

# 오늘 환율 수집 트리거
curl -X POST http://localhost:8000/api/exchange-rates/fetch/

# 특정 날짜 환율 수집
curl -X POST http://localhost:8000/api/exchange-rates/fetch/dates/2026-01-10/
```

3. DRF Browsable API:
   - 브라우저에서 `http://localhost:8000/api/exchange-rates/` 접속
   - 인터랙티브 API 브라우저로 테스트

---

## 향후 계획

> [!NOTE]
> HON-6 완료 후 고려 사항
> - 인증/권한 설정 (Token Auth, API Key 등)
> - Rate Limiting
> - API 문서화 (drf-spectacular 등)
