from datetime import date
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

def validateMonth(value):
    if not (1 <= value <= 12):
        raise ValidationError(
            "Expiry month of credit/debit/prepaid cards must be in the range 1 <= month <= 12"
        )
    return value

def validateYear(value):
    if not (0 <= value <= 99):
        raise ValidationError(
            "Expiry year of credit/debit/prepaid cards must be in the range 0 <= year <= 99"
        )
    return value

    
class CreditCard(models.Model):
    number = models.CharField(
        max_length=17, default="4111111111111111"
    )
    last_4 = models.CharField(max_length=4,)
    
    # Constants for card brands that ACME supports
    TYPE_AMEX = "amex"
    TYPE_DISCOVER = "discover"
    TYPE_MASTERCARD = "mastercard"
    TYPE_VISA = "visa"
    CARD_BRAND_CHOICE = (
        (TYPE_AMEX, "Amex"),
        (TYPE_DISCOVER, "Discover"),
        (TYPE_MASTERCARD, "Mastercard"),
        (TYPE_VISA, "Visa"),
    )

    brand = models.CharField(max_length=255, choices=CARD_BRAND_CHOICE)
    exp_month = models.PositiveSmallIntegerField(validators=[validateMonth])
    exp_year = models.PositiveSmallIntegerField(validators=[validateYear]) # 2 digits, e.g. 26 instead of 2026

class EBT(models.Model):
    number = models.CharField(
        max_length=19, default="123456789"
    )
    last_4 = models.CharField(max_length=4)
    STATE_AP = "AndraPradesh"
    STATE_TS = "Telangana"
    STATE_MP = "MadhyaPradesh"
    STATE_DEL = "Delhi"
    EBT_CHOICE = (
        (STATE_AP, "AndraPradesh"),
        (STATE_TS, "Telangana"),
        (STATE_MP, "MadhyaPradesh"),
        (STATE_DEL, "Delhi"),
    )
    issue_month = models.PositiveSmallIntegerField(validators=[validateMonth])
    issue_year = models.PositiveSmallIntegerField(validators=[validateYear]) # 2 digits, e.g. 26 instead of 2026
    state = models.CharField(max_length=255, choices=EBT_CHOICE)
    


class Order(models.Model):
    # The total amount which needs to be paid by the customer, including taxes and fees
    order_total = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(0)],
    )

    # Constants for order statuses
    TYPE_DRAFT = "draft"
    TYPE_FAILED = "failed"
    TYPE_SUCCEEDED = "succeeded"
    ORDER_STATUS_CHOICE = (
        (TYPE_DRAFT, "draft"),
        (TYPE_FAILED, "failed"),
        (TYPE_SUCCEEDED, "succeeded"),
    )

    status = models.CharField(
        max_length=10, 
        choices=ORDER_STATUS_CHOICE, 
        default=TYPE_DRAFT
    )

    success_date = models.DateTimeField(
        "Date when an order was successfully charged",
        null=True,
        blank=True,
    )

    # UNCOMMENT THIS FIELD TO GET STARTED!
    #
    # The amount which can be paid for with EBT. It's not necessarily true that the
    # entire ebt_total will be satisfied with EBT tender.
    ebt_total = models.DecimalField(
        decimal_places=2, max_digits=12, validators=[MinValueValidator(0)]
    )

class Payment(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, db_index=True
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(0),],
    )

    description = models.CharField(max_length=255)
    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.CASCADE,
        related_name='credit_card_payments',
        null=True,
        blank=True,
    )
    
    ebt = models.ForeignKey(
        EBT,
        on_delete=models.CASCADE,
        related_name='ebt_payments',
        null=True,
        blank=True,
    )
    
    ACTIVE_PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('ebt', 'EBT'),
    ]
    payment_method = models.CharField(
        max_length=24,
        choices=ACTIVE_PAYMENT_METHOD_CHOICES,
    )

    TYPE_REQ_CONF = "requires_confirmation"
    TYPE_SUCCEEDED = "succeeded"
    TYPE_FAILED = "failed"
    PAYMENT_STATUS_CHOICE = (
        (TYPE_REQ_CONF, "requires_confirmation"),
        (TYPE_SUCCEEDED, "succeeded"),
        (TYPE_FAILED, "failed"),
    )
    status = models.CharField(
        max_length=24, 
        choices=PAYMENT_STATUS_CHOICE, 
        default='requires_confirmation',
    )

    success_date = models.DateTimeField(
        "Date when a payment was successfully charged",
        null=True,
        blank=True,
    )

    last_processing_error = models.TextField(null=True, blank=True)
