from django.db import models


class ExchangeRate(models.Model):
    """환율 정보 모델"""

    code = models.CharField("통화 코드", max_length=10, db_index=True)  # USD, EUR, JPY 등
    name = models.CharField("통화명", max_length=50)  # 미국 달러, 유로 등

    # 환율 정보
    base_rate = models.DecimalField("매매기준율", max_digits=15, decimal_places=4)
    cash_buy_rate = models.DecimalField("현찰 살 때", max_digits=15, decimal_places=4, null=True, blank=True)
    cash_sell_rate = models.DecimalField("현찰 팔 때", max_digits=15, decimal_places=4, null=True, blank=True)
    remit_send_rate = models.DecimalField("송금 보낼 때", max_digits=15, decimal_places=4, null=True, blank=True)
    remit_receive_rate = models.DecimalField("송금 받을 때", max_digits=15, decimal_places=4, null=True, blank=True)

    # 메타 정보
    date = models.DateField("고시일", db_index=True)
    fetched_at = models.DateTimeField("수집 시간", auto_now_add=True)

    class Meta:
        verbose_name = "환율"
        verbose_name_plural = "환율 목록"
        ordering = ["-date", "code"]
        unique_together = ["code", "date"]
        indexes = [
            models.Index(fields=["code", "date"]),
        ]

    def __str__(self):
        return f"{self.code} ({self.date}): {self.base_rate}"
