from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Account(models.Model):
    ACCOUNT_TYPES = [
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("mobile_banking", "Mobile Banking"),
        ("card", "Card"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPES, default="cash")
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def current_balance(self):
        deposit = self.transactions.filter(transaction_type="deposit").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")

        expense = self.transactions.filter(transaction_type="expense").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")

        return self.opening_balance + deposit - expense


class Category(models.Model):
    CATEGORY_TYPES = [
        ("deposit", "Deposit"),
        ("expense", "Expense"),
    ]

    name = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["transaction_type", "name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.get_transaction_type_display()})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("expense", "Expense"),
    ]

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="transactions",
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(default=timezone.localdate)
    note = models.TextField(blank=True, null=True)
    attachment = models.FileField(
        upload_to="money_tracker/attachments/",
        blank=True,
        null=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="money_transactions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({"amount": "Amount must be greater than zero."})

        if self.category and self.category.transaction_type != self.transaction_type:
            raise ValidationError({
                "category": "Category type must match transaction type."
            })