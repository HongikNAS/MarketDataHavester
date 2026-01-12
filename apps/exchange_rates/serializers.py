"""
환율 데이터 Serializer
"""

from rest_framework import serializers

from .models import ExchangeRate


class ExchangeRateSerializer(serializers.ModelSerializer):
    """환율 정보 Serializer"""

    class Meta:
        model = ExchangeRate
        fields = [
            "id",
            "code",
            "name",
            "base_rate",
            "cash_buy_rate",
            "cash_sell_rate",
            "remit_send_rate",
            "remit_receive_rate",
            "date",
            "fetched_at",
        ]
        read_only_fields = ["id", "fetched_at"]
