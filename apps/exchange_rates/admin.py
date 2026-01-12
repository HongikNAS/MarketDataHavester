from django.contrib import admin

from .models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "base_rate", "date", "fetched_at"]
    list_filter = ["code", "date"]
    search_fields = ["code", "name"]
    date_hierarchy = "date"
    ordering = ["-date", "code"]
    readonly_fields = ["fetched_at"]
