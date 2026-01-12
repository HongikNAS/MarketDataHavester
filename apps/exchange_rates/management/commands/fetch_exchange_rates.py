"""
환율 데이터 수집 관리 커맨드

사용법:
    python manage.py fetch_exchange_rates           # 오늘 환율 수집
    python manage.py fetch_exchange_rates --date 2024-01-15  # 특정 날짜 수집
"""

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from apps.exchange_rates.services import KoreaEximAPIError, save_exchange_rates


class Command(BaseCommand):
    help = "한국수출입은행 API에서 환율 데이터를 수집합니다"

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="수집할 날짜 (YYYY-MM-DD 형식, 기본값: 오늘)",
        )

    def handle(self, *args, **options):
        date_str = options.get("date")
        search_date = None

        if date_str:
            try:
                search_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise CommandError(f"잘못된 날짜 형식입니다: {date_str} (YYYY-MM-DD 형식 필요)")

        try:
            count = save_exchange_rates(search_date)
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"환율 데이터 {count}건 저장 완료"))
            else:
                self.stdout.write(self.style.WARNING("저장된 환율 데이터가 없습니다 (주말/공휴일 가능성)"))
        except KoreaEximAPIError as e:
            raise CommandError(str(e))
