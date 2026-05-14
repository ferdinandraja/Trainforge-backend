from django.contrib import admin
from .models import Subscription


@admin.action(description="Archive selected subscriptions")
def archive_subscriptions(modeladmin, request, queryset):
    queryset.update(is_archived=True, status="archived")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "trainer",
        "plan_name",
        "status",
        "monthly_price",
        "start_date",
        "end_date",
        "is_archived",
        "created_at",
    )

    list_filter = (
        "plan_name",
        "status",
        "is_archived",
        "start_date",
    )

    search_fields = (
        "trainer__username",
        "trainer__email",
        "plan_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    list_per_page = 10

    actions = [archive_subscriptions]

    def has_delete_permission(self, request, obj=None):
        return False
