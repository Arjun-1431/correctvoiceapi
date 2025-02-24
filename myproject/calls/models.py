
from django.db import models

class CallDetail(models.Model):
    phone_number = models.CharField(max_length=15)
    call_status = models.CharField(max_length=10)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.phone_number} - {self.call_status} at {self.timestamp}"


class Balance(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self):
        return f"Balance: {self.amount}"

    def save(self, *args, **kwargs):
        if Balance.objects.exists() and not self.pk:
            raise ValueError("Only one balance entry is allowed. Please update the existing balance.")
        super().save(*args, **kwargs)