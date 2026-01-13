"""
환율 API Views
"""

from datetime import date, datetime

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ExchangeRate
from .serializers import ExchangeRateSerializer
from .services import KoreaEximAPIError, save_exchange_rates


class ExchangeRateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    환율 정보 ViewSet

    제공하는 엔드포인트:
    - GET /api/exchange-rates/ : 환율 목록 조회 (필터링/페이지네이션)
    - GET /api/exchange-rates/{code}/ : 특정 통화 전체 이력
    - GET /api/exchange-rates/{code}/dates/{date}/ : 특정 통화 + 날짜
    - POST /api/exchange-rates/fetch/ : 오늘 환율 수집
    - POST /api/exchange-rates/fetch/dates/{date}/ : 특정 날짜 환율 수집
    """

    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer

    def get_queryset(self):
        """필터링 파라미터 적용"""
        queryset = super().get_queryset()

        # 통화 코드 필터
        code = self.request.query_params.get("code")
        if code:
            queryset = queryset.filter(code=code.upper())

        # 날짜 필터
        date_param = self.request.query_params.get("date")
        if date_param:
            queryset = queryset.filter(date=date_param)

        # 날짜 범위 필터
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    @action(detail=False, methods=["get"], url_path=r"(?P<code>[A-Z]+)")
    def by_code(self, request, code=None):
        """특정 통화 코드의 전체 환율 이력 조회"""
        queryset = self.get_queryset().filter(code=code.upper())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path=r"(?P<code>[A-Z]+)/dates/(?P<rate_date>\d{4}-\d{2}-\d{2})")
    def by_code_and_date(self, request, code=None, rate_date=None):
        """특정 통화 코드 + 날짜의 환율 조회"""
        try:
            exchange_rate = ExchangeRate.objects.get(code=code.upper(), date=rate_date)
            serializer = self.get_serializer(exchange_rate)
            return Response(serializer.data)
        except ExchangeRate.DoesNotExist:
            return Response(
                {"error": f"{code} 통화의 {rate_date} 환율 데이터가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["post"], url_path="fetch")
    def fetch_today(self, request):
        """오늘 날짜 환율 데이터 수집"""
        try:
            count = save_exchange_rates()
            return Response(
                {
                    "message": f"오늘({date.today()}) 환율 데이터 {count}건 수집 완료",
                    "date": str(date.today()),
                    "count": count,
                }
            )
        except KoreaEximAPIError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    @action(detail=False, methods=["post"], url_path=r"fetch/dates/(?P<fetch_date>\d{4}-\d{2}-\d{2})")
    def fetch_by_date(self, request, fetch_date=None):
        """특정 날짜 환율 데이터 수집"""
        try:
            target_date = datetime.strptime(fetch_date, "%Y-%m-%d").date()
            count = save_exchange_rates(target_date)
            return Response(
                {
                    "message": f"{fetch_date} 환율 데이터 {count}건 수집 완료",
                    "date": fetch_date,
                    "count": count,
                }
            )
        except ValueError:
            return Response(
                {"error": "날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력하세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KoreaEximAPIError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
