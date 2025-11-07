from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, CookProfile, Booking, Review


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")


@admin.register(CookProfile)
class CookProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "cuisine", "experience_years", "hourly_rate", "average_rating")
    search_fields = ("user__username", "cuisine", "dishes", "location")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "cook", "date", "time", "status", "payment_status")
    list_filter = ("status", "payment_status", "date")
    search_fields = ("customer__username", "cook__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "cook", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("customer__username", "cook__username", "comment")

