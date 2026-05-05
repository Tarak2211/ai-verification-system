# Stockist and Product Matching Models
from django.db import models
from django.core.validators import MinValueValidator
from .models import State, CustomUser


class Stockist(models.Model):
    """Stockist/Distributor information"""
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='stockists')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stockist'
        ordering = ['code']
        indexes = [
            models.Index(fields=['state', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Division(models.Model):
    """Product divisions (AESTHETIC, COSMECEUTICAL, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'division'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Master product catalog"""
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    division = models.ForeignKey(Division, on_delete=models.PROTECT, related_name='products')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product'
        ordering = ['code']
        indexes = [
            models.Index(fields=['division', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class StockistProductMatch(models.Model):
    """Product matching records between PDF and Excel"""
    
    VALIDATION_CHOICES = [
        ('MATCHED', 'Matched'),
        ('QUANTITY_MISMATCH', 'Quantity Mismatch'),
        ('DIVISION_MISMATCH', 'Division Mismatch'),
        ('QUANTITY_AND_DIVISION_MISMATCH', 'Quantity and Division Mismatch'),
        ('PRODUCT_NOT_FOUND', 'Product Not Found'),
    ]
    
    MATCH_METHOD_CHOICES = [
        ('EXACT', 'Exact'),
        ('FUZZY', 'Fuzzy Match'),
    ]
    
    # Reference data
    row_index = models.IntegerField()
    stockist = models.ForeignKey(Stockist, on_delete=models.CASCADE, related_name='product_matches')
    month_year = models.CharField(max_length=20, db_index=True)  # e.g., "Oct-2025"
    
    # PDF data
    pdf_division = models.CharField(max_length=100, blank=True)
    pdf_product = models.CharField(max_length=200, blank=True)
    pdf_closing = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Excel data
    excel_division = models.ForeignKey(Division, on_delete=models.PROTECT, null=True, blank=True)
    excel_product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    excel_closing = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Matching results
    match_method = models.CharField(max_length=20, choices=MATCH_METHOD_CHOICES, blank=True)
    variance = models.IntegerField(default=0)
    validation = models.CharField(max_length=50, choices=VALIDATION_CHOICES, db_index=True)
    label = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stockist_product_match'
        ordering = ['-month_year', 'stockist', 'row_index']
        indexes = [
            models.Index(fields=['stockist', 'month_year']),
            models.Index(fields=['validation', 'month_year']),
            models.Index(fields=['month_year', 'stockist', 'row_index']),
        ]
        unique_together = [['stockist', 'month_year', 'row_index']]
    
    def __str__(self):
        return f"{self.stockist.code} - {self.month_year} - Row {self.row_index}"
    
    @property
    def state(self):
        """Get state from stockist for easy filtering"""
        return self.stockist.state
