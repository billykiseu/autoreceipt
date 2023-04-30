from django.db import models

class Transaction(models.Model):
    name = models.CharField(max_length=255)
    transaction_type = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()

    def __str__(self):
        return self.name
