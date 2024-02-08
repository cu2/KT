from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from ktapp import models
from ktapp import forms as kt_forms


admin.site.unregister(Group)


@admin.register(models.Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ["given_at", "money", "given_by", "comment", "tshirt"]
    fields = ["given_at", "money", "given_by", "comment", "tshirt"]
    raw_id_fields = ["given_by"]


@admin.register(models.EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ["sent_at", "title", "subject", "recipients"]
    list_display_links = ["title"]
    fields = ["sent_at", "title", "subject", "recipients", "pm_message"]


@admin.register(models.KTUser)
class KTUserAdmin(UserAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "is_editor",
        "is_ex_editor",
        "is_moderator",
        "is_ex_moderator",
        "is_inner_staff",
        "is_staff",
        "is_reliable",
        "is_game_master",
    ]
    list_display_links = ["username"]
    list_filter = [
        "is_editor",
        "is_ex_editor",
        "is_moderator",
        "is_ex_moderator",
        "is_inner_staff",
        "is_staff",
        "is_reliable",
        "is_game_master",
    ]
    search_fields = ["username", "email"]
    ordering = ["id"]

    form = kt_forms.UserChangeForm
    fieldsets = [
        (None, {"fields": ["username", "email"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_editor",
                    "is_ex_editor",
                    "is_moderator",
                    "is_ex_moderator",
                    "is_inner_staff",
                    "is_staff",
                    "is_reliable",
                    "is_game_master",
                ]
            },
        ),
    ]

    # disable add, delete, bulk delete
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.ServerCost)
class ServerCostAdmin(admin.ModelAdmin):
    list_display = [
        "year",
        "actual_cost",
        "planned_cost",
        "opening_balance",
        "actual_cost_estimated",
    ]
    fields = [
        "year",
        "actual_cost",
        "planned_cost",
        "opening_balance",
        "actual_cost_estimated",
    ]
