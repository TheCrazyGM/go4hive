from django.contrib import admin

from .models import BlacklistedUser, HiveCommunity


@admin.register(HiveCommunity)
class HiveCommunityAdmin(admin.ModelAdmin):
    list_display = ("name", "identifier", "title", "updated_at")
    search_fields = ("name", "identifier", "title")


@admin.register(BlacklistedUser)
class BlacklistedUserAdmin(admin.ModelAdmin):
    list_display = ("username", "created_at")
    search_fields = ("username",)
