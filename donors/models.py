# In donors/models.py

from django.db import models

class Donor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    total_donated = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name