"""
환율 앱 테스트
"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.exchange_rates.models import ExchangeRate
from apps.exchange_rates.services import (
    KoreaEximAPIError,
    fetch_exchange_rates,
    parse_rate,
    save_exchange_rates,
)


class ParseRateTestCase(TestCase):
    """환율 파싱 테스트"""

    def test_parse_rate_with_comma(self):
        """쉼표가 포함된 환율 파싱"""
        result = parse_rate("1,432.50")
        self.assertEqual(result, Decimal("1432.50"))

    def test_parse_rate_without_comma(self):
        """쉼표가 없는 환율 파싱"""
        result = parse_rate("100.25")
        self.assertEqual(result, Decimal("100.25"))

    def test_parse_rate_none(self):
        """None 값 처리"""
        result = parse_rate(None)
        self.assertIsNone(result)

    def test_parse_rate_empty_string(self):
        """빈 문자열 처리"""
        result = parse_rate("")
        self.assertIsNone(result)


class ExchangeRateModelTestCase(TestCase):
    """환율 모델 테스트"""

    def test_create_exchange_rate(self):
        """환율 레코드 생성"""
        rate = ExchangeRate.objects.create(
            code="USD",
            name="미국 달러",
            base_rate=Decimal("1432.50"),
            date=date(2024, 1, 15),
        )
        self.assertEqual(rate.code, "USD")
        self.assertEqual(rate.name, "미국 달러")
        self.assertEqual(rate.base_rate, Decimal("1432.50"))

    def test_exchange_rate_str(self):
        """__str__ 메서드 테스트"""
        rate = ExchangeRate.objects.create(
            code="USD",
            name="미국 달러",
            base_rate=Decimal("1432.50"),
            date=date(2024, 1, 15),
        )
        self.assertIn("USD", str(rate))
        self.assertIn("1432.50", str(rate))

    def test_unique_together(self):
        """code + date 유니크 제약 테스트"""
        ExchangeRate.objects.create(
            code="USD",
            name="미국 달러",
            base_rate=Decimal("1432.50"),
            date=date(2024, 1, 15),
        )
        # 같은 code + date로 생성 시도하면 IntegrityError 발생
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            ExchangeRate.objects.create(
                code="USD",
                name="미국 달러",
                base_rate=Decimal("1433.00"),
                date=date(2024, 1, 15),
            )


class FetchExchangeRatesTestCase(TestCase):
    """API 호출 테스트"""

    def test_fetch_without_api_key(self):
        """API 키 없이 호출 시 에러"""
        with self.settings(KOREAEXIM_API_KEY=""):
            with self.assertRaises(KoreaEximAPIError) as context:
                fetch_exchange_rates()
            self.assertIn("API_KEY", str(context.exception))

    @patch("apps.exchange_rates.services.requests.get")
    def test_fetch_success(self, mock_get):
        """API 호출 성공 테스트"""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "cur_unit": "USD",
                "cur_nm": "미국 달러",
                "deal_bas_r": "1,432.50",
                "bkpr": "1,460.00",
                "kftc_bkpr": "1,405.00",
                "tts": "1,447.00",
                "ttb": "1,418.00",
            }
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with self.settings(KOREAEXIM_API_KEY="test_key"):
            result = fetch_exchange_rates(date(2024, 1, 15))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cur_unit"], "USD")

    @patch("apps.exchange_rates.services.requests.get")
    def test_fetch_empty_response(self, mock_get):
        """빈 응답 (주말/공휴일) 테스트"""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with self.settings(KOREAEXIM_API_KEY="test_key"):
            result = fetch_exchange_rates(date(2024, 1, 14))  # 일요일

        self.assertEqual(result, [])


class SaveExchangeRatesTestCase(TestCase):
    """환율 저장 테스트"""

    @patch("apps.exchange_rates.services.fetch_exchange_rates")
    def test_save_exchange_rates(self, mock_fetch):
        """환율 저장 테스트"""
        mock_fetch.return_value = [
            {
                "cur_unit": "USD",
                "cur_nm": "미국 달러",
                "deal_bas_r": "1,432.50",
                "bkpr": "1,460.00",
                "kftc_bkpr": "1,405.00",
                "tts": "1,447.00",
                "ttb": "1,418.00",
            },
            {
                "cur_unit": "EUR",
                "cur_nm": "유로",
                "deal_bas_r": "1,550.00",
                "bkpr": "1,580.00",
                "kftc_bkpr": "1,520.00",
                "tts": "1,565.00",
                "ttb": "1,535.00",
            },
        ]

        count = save_exchange_rates(date(2024, 1, 15))

        self.assertEqual(count, 2)
        self.assertEqual(ExchangeRate.objects.count(), 2)

        usd = ExchangeRate.objects.get(code="USD")
        self.assertEqual(usd.name, "미국 달러")
        self.assertEqual(usd.base_rate, Decimal("1432.50"))

    @patch("apps.exchange_rates.services.fetch_exchange_rates")
    def test_save_updates_existing(self, mock_fetch):
        """기존 데이터 업데이트 테스트"""
        # 기존 데이터 생성
        ExchangeRate.objects.create(
            code="USD",
            name="미국 달러",
            base_rate=Decimal("1430.00"),
            date=date(2024, 1, 15),
        )

        mock_fetch.return_value = [
            {
                "cur_unit": "USD",
                "cur_nm": "미국 달러",
                "deal_bas_r": "1,432.50",
            },
        ]

        count = save_exchange_rates(date(2024, 1, 15))

        self.assertEqual(count, 1)
        self.assertEqual(ExchangeRate.objects.count(), 1)

        usd = ExchangeRate.objects.get(code="USD")
        self.assertEqual(usd.base_rate, Decimal("1432.50"))  # 업데이트됨
