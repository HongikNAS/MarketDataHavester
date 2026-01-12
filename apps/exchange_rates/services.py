"""
한국수출입은행 Open API를 통한 환율 데이터 수집 서비스
"""

import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from django.conf import settings

from .models import ExchangeRate

logger = logging.getLogger(__name__)


class KoreaEximAPIError(Exception):
    """수출입은행 API 호출 오류"""

    pass


def parse_rate(value: str | None) -> Decimal | None:
    """환율 문자열을 Decimal로 변환 (쉼표 제거)"""
    if not value:
        return None
    try:
        # 쉼표 제거 후 Decimal 변환
        return Decimal(value.replace(",", ""))
    except (InvalidOperation, AttributeError):
        return None


def fetch_exchange_rates(search_date: date | None = None) -> list[dict[str, Any]]:
    """
    수출입은행 API에서 환율 데이터를 가져옵니다.

    Args:
        search_date: 조회할 날짜 (기본값: 오늘)

    Returns:
        API 응답 데이터 리스트

    Raises:
        KoreaEximAPIError: API 호출 실패 시
    """
    api_key = settings.KOREAEXIM_API_KEY
    if not api_key:
        raise KoreaEximAPIError("KOREAEXIM_API_KEY가 설정되지 않았습니다.")

    if search_date is None:
        search_date = date.today()

    params = {
        "authkey": api_key,
        "searchdate": search_date.strftime("%Y%m%d"),
        "data": "AP01",  # 환율 데이터
    }

    try:
        response = requests.get(settings.KOREAEXIM_API_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise KoreaEximAPIError(f"API 호출 실패: {e}") from e

    data = response.json()

    # API 응답이 빈 리스트인 경우 (주말/공휴일 등)
    if not data:
        logger.info(f"{search_date} 환율 데이터가 없습니다 (주말/공휴일 가능성)")
        return []

    # API 에러 응답 확인
    if isinstance(data, dict) and data.get("result") == 0:
        raise KoreaEximAPIError(f"API 오류: {data}")

    return data


def save_exchange_rates(search_date: date | None = None) -> int:
    """
    수출입은행 API에서 환율을 가져와 DB에 저장합니다.

    Args:
        search_date: 조회할 날짜 (기본값: 오늘)

    Returns:
        저장된 환율 데이터 개수
    """
    if search_date is None:
        search_date = date.today()

    data = fetch_exchange_rates(search_date)

    if not data:
        return 0

    saved_count = 0

    for item in data:
        code = item.get("cur_unit", "").strip()
        if not code:
            continue

        # 기존 데이터가 있으면 업데이트, 없으면 생성
        exchange_rate, created = ExchangeRate.objects.update_or_create(
            code=code,
            date=search_date,
            defaults={
                "name": item.get("cur_nm", ""),
                "base_rate": parse_rate(item.get("deal_bas_r")),
                "cash_buy_rate": parse_rate(item.get("bkpr")),
                "cash_sell_rate": parse_rate(item.get("kftc_bkpr")),
                "remit_send_rate": parse_rate(item.get("tts")),
                "remit_receive_rate": parse_rate(item.get("ttb")),
            },
        )

        action = "생성" if created else "업데이트"
        logger.debug(f"{code} {search_date} 환율 {action}: {exchange_rate.base_rate}")
        saved_count += 1

    logger.info(f"{search_date} 환율 데이터 {saved_count}건 저장 완료")
    return saved_count
