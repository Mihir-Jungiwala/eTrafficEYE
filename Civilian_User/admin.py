from django.contrib import admin
from .models import Evidence
from django.utils.html import format_html

# 🔥 IMPORT POLICE MODEL
from Police_User.models import Police_Evidence_Review


class EvidenceAdmin(admin.ModelAdmin):

    fields = (

        'username_display',

        'complaint_no',

        'violations',

        'address',
        'city',
        'state',
        'pincode',
        'country',

        'datetime',

        'vehicle_number',
        'description',

        'image1_full',
        'image2_full',
        'image3_full',

        # 🔥 NEW REVIEW FIELDS
        'review_status',
        'selected_violations_display',
        'penalty_display',
        'reward_display',
        'remark_display',
    )

    readonly_fields = (
        'username_display',
        'image1_full',
        'image2_full',
        'image3_full',

        # 🔥 NEW READONLY
        'review_status',
        'selected_violations_display',
        'penalty_display',
        'reward_display',
        'remark_display',
    )

    list_display = (
        'complaint_no',
        'username_display',
        'city',
        'pincode',
        'review_status',
    )

    search_fields = (
        'complaint_no',
        'vehicle_number',
        'city',
        'user__username'
    )

    list_filter = (
        'city',
        'state',
    )

    ordering = ('-id',)

    # -------- USERNAME --------
    def username_display(self, obj):
        return obj.user.username
    username_display.short_description = "Username"

    # -------- IMAGE 1 --------
    def image1_full(self, obj):
        if obj.image1:
            return format_html(
                '<img src="{}" width="300" style="margin:5px;border-radius:10px;" />',
                obj.image1.url
            )
        return "No Image"
    image1_full.short_description = "Image 1"

    # -------- IMAGE 2 --------
    def image2_full(self, obj):
        if obj.image2:
            return format_html(
                '<img src="{}" width="300" style="margin:5px;border-radius:10px;" />',
                obj.image2.url
            )
        return "No Image"
    image2_full.short_description = "Image 2"

    # -------- IMAGE 3 --------
    def image3_full(self, obj):
        if obj.image3:
            return format_html(
                '<img src="{}" width="300" style="margin:5px;border-radius:10px;" />',
                obj.image3.url
            )
        return "No Image"
    image3_full.short_description = "Image 3"

    # 🔥 GET LATEST REVIEW
    def get_latest_review(self, obj):
        return Police_Evidence_Review.objects.filter(evidence=obj).order_by('-id').first()

    # -------- STATUS --------
    def review_status(self, obj):
        review = self.get_latest_review(obj)
        return review.status if review else "Pending"
    review_status.short_description = "Status"

    # -------- SELECTED VIOLATIONS --------
    def selected_violations_display(self, obj):
        review = self.get_latest_review(obj)
        return review.selected_violations if review else "-"
    selected_violations_display.short_description = "Selected Violations"

    # -------- PENALTY --------
    def penalty_display(self, obj):
        review = self.get_latest_review(obj)
        return f"₹{review.penalty_amount}" if review else "₹0"
    penalty_display.short_description = "Penalty Amount"

    # -------- REWARD --------
    def reward_display(self, obj):
        review = self.get_latest_review(obj)
        return f"₹{review.reward_amount}" if review else "₹0"
    reward_display.short_description = "Reward Amount"

    # -------- REMARK --------
    def remark_display(self, obj):
        review = self.get_latest_review(obj)
        return review.remark if review else "-"
    remark_display.short_description = "Police Remark"


admin.site.register(Evidence, EvidenceAdmin)