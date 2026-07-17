from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Police_Evidence_Review(models.Model):

    # 🔥 FIXED FOREIGN KEY (ADD YOUR APP NAME HERE)
    evidence = models.ForeignKey('Civilian_User.Evidence', on_delete=models.CASCADE, related_name='reviews')

    police = models.ForeignKey(User, on_delete=models.CASCADE)

    # 🔥 REVIEW DATA
    selected_violations = models.TextField(blank=True, null=True)
    penalty_amount = models.IntegerField(default=0)
    reward_amount = models.IntegerField(default=0)
    remark = models.TextField(blank=True, null=True)

    # 🔥 STATUS
    status = models.CharField(max_length=20, choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ], default='pending')

    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.evidence.complaint_no} - {self.status}"