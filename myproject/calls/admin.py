from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(CallDetail)
class CallDetailAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'call_status', 'timestamp')
    search_fields = ('phone_number', 'call_status')
    list_filter = ('call_status', 'timestamp')


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('amount',)

    def has_add_permission(self, request):
        # Disable add button if a balance entry already exists
        if Balance.objects.exists():
            return False
        return super().has_add_permission(request)