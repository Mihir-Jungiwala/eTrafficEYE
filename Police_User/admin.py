from django.contrib import admin
from .models import Police_Evidence_Review


class PoliceEvidenceReviewAdmin(admin.ModelAdmin):

    list_display = (
        'evidence',
        'police',
        'status',
        'penalty_amount',
        'reward_amount',
        'reviewed_at',
    )

    search_fields = (
        'evidence__complaint_no',
        'police__username',
    )

    list_filter = (
        'status',
        'reviewed_at',
    )

    ordering = ('-id',)


admin.site.register(Police_Evidence_Review, PoliceEvidenceReviewAdmin)