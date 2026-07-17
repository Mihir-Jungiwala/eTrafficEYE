from django.contrib import admin
from .models import Authentication
from django.utils.html import format_html


class AuthenticationAdmin(admin.ModelAdmin):

    fields = (
        'profile_preview',

        'full_name',
        'username_display',
        'email_display',
        'mobile_number',

        'role',
        'status',   # ✅ THIS gives dropdown (True/False)

        'civilian_id_card_name',
        'police_id_number',

        'id_front_preview',
        'id_back_preview',
    )

    readonly_fields = (
        'profile_preview',
        'username_display',
        'email_display',
        'id_front_preview',
        'id_back_preview',
    )

    list_display = (
        'username_display',
        'full_name',
        'mobile_number',
        'role',
        'status'   # ✅ simple True/False column
    )

    search_fields = ('user__username', 'full_name', 'mobile_number')
    list_filter = ('role', 'status')

    # -------- USERNAME --------
    def username_display(self, obj):
        return obj.user.username

    # -------- EMAIL --------
    def email_display(self, obj):
        return obj.user.email

    # -------- PROFILE IMAGE --------
    def profile_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="150" style="border-radius:10px;" />',
                obj.profile_image.url
            )
        return "No Image"

    # -------- FRONT IMAGE --------
    def id_front_preview(self, obj):
        if obj.id_image_front:
            return format_html(
                '<img src="{}" width="150" style="border-radius:10px;" />',
                obj.id_image_front.url
            )
        return "No Image"

    # -------- BACK IMAGE --------
    def id_back_preview(self, obj):
        if obj.id_image_back:
            return format_html(
                '<img src="{}" width="150" style="border-radius:10px;" />',
                obj.id_image_back.url
            )
        return "No Image"


admin.site.register(Authentication, AuthenticationAdmin)