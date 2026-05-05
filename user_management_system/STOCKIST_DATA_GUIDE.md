# Stockist Product Matching Data System

## Overview

This system allows you to import and manage stockist product matching data with state-based access control. Users can only view data for stockists in their assigned states.

## Features

- **State-based Access Control**: Users only see data for their assigned states
- **Incremental Loading**: Import only new records, skip existing ones
- **Product Matching Validation**: Track matched, mismatched, and missing products
- **Multi-division Support**: Handle different product divisions (AESTHETIC, COSMECEUTICAL, etc.)
- **Comprehensive Reporting**: Dashboard, mismatch reports, and detailed views

## Database Models

### 1. Stockist
- Stores distributor/stockist information
- Linked to State for access control
- Fields: code, name, state, is_active

### 2. Division
- Product divisions (AESTHETIC, COSMECEUTICAL, DERMATOLOGICAL, etc.)
- Fields: name, is_active

### 3. Product
- Master product catalog
- Fields: code, name, division, is_active

### 4. StockistProductMatch
- Product matching records between PDF and Excel
- Tracks validation status, variances, and mismatches
- Fields: stockist, month_year, pdf_data, excel_data, validation, variance

## Setup Instructions

### 1. Run Migrations

```bash
cd user_management_system
python manage.py migrate
```

### 2. Prepare Your CSV Data

Your CSV file should have these columns:
- Row Index
- Stockist Code
- state_name
- Stockist Name
- month_year
- PDF Division
- Excel Division
- PDF Product
- Product Code
- Excel Product
- Match Method
- PDF Closing
- Excel Closing
- Variance
- Validation
- Label
- Description

### 3. Import Data

**Full Import (first time):**
```bash
python manage.py import_stockist_data path/to/your/data.csv
```

**Incremental Import (skip existing records):**
```bash
python manage.py import_stockist_data path/to/your/data.csv --incremental
```

**Filter by Month:**
```bash
python manage.py import_stockist_data path/to/your/data.csv --month-year "Oct-2025"
```

**Incremental + Month Filter:**
```bash
python manage.py import_stockist_data path/to/your/data.csv --incremental --month-year "Oct-2025"
```

## Access Control

### User Roles

1. **Super Admin**
   - Can view ALL stockist data across all states
   - Full access to all features

2. **Sub-Admin**
   - Can view data for their assigned states only
   - If no states assigned, sees all states

3. **User**
   - Can view data for their assigned states only
   - Must have at least one state assigned

### How It Works

The system uses your existing RBAC (Role-Based Access Control) with state permissions:

```python
# Get user's accessible states
accessible_states = user.get_accessible_states()

# Filter stockist data by user's states
if user.is_superuser:
    data = StockistProductMatch.objects.all()
else:
    data = StockistProductMatch.objects.filter(
        stockist__state__in=accessible_states
    )
```

## URL Configuration

Add these URLs to your `urls.py`:

```python
from accounts import stockist_views

urlpatterns = [
    # ... existing patterns ...
    
    # Stockist data URLs
    path('stockist/dashboard/', stockist_views.stockist_dashboard, name='stockist_dashboard'),
    path('stockist/list/', stockist_views.stockist_list, name='stockist_list'),
    path('stockist/<str:stockist_code>/', stockist_views.stockist_detail, name='stockist_detail'),
    path('stockist/reports/mismatches/', stockist_views.product_mismatch_report, name='product_mismatch_report'),
]
```

## Views Available

### 1. Stockist Dashboard (`/stockist/dashboard/`)
- Overview of all product matching data
- Statistics: matched, mismatched, not found
- Filters: month, validation status, division
- **Access**: Filtered by user's assigned states

### 2. Stockist List (`/stockist/list/`)
- List of all stockists
- Paginated view (50 per page)
- **Access**: Only stockists in user's assigned states

### 3. Stockist Detail (`/stockist/<code>/`)
- Detailed product matching data for a specific stockist
- Shows all matching records with filters
- Paginated view (100 per page)
- **Access**: Only if stockist is in user's assigned states

### 4. Mismatch Report (`/stockist/reports/mismatches/`)
- Shows all non-matched records
- Filters by validation type
- Statistics by mismatch type
- **Access**: Only mismatches from user's assigned states

## Validation Types

- **MATCHED**: Product matched perfectly with zero variance
- **QUANTITY_MISMATCH**: Product matched but closing quantity differs
- **DIVISION_MISMATCH**: Product matched but division name differs
- **QUANTITY_AND_DIVISION_MISMATCH**: Both quantity AND division differ
- **PRODUCT_NOT_FOUND**: Product does not exist in Excel master file

## Example Usage

### Scenario 1: Super Admin
```python
# Super Admin can see everything
user = CustomUser.objects.get(username='admin')
user.is_superuser  # True

# Gets all stockist data
all_data = StockistProductMatch.objects.all()
```

### Scenario 2: Gujarat Sub-Admin
```python
# Sub-Admin assigned to Gujarat
user = CustomUser.objects.get(username='gujarat_admin')
user.role  # 'SUB_ADMIN'
user.get_accessible_states()  # [<State: Gujarat>]

# Only sees Gujarat stockist data
gujarat_data = StockistProductMatch.objects.filter(
    stockist__state__name='Gujarat'
)
```

### Scenario 3: Multi-State User
```python
# User assigned to Delhi, UP, Rajasthan
user = CustomUser.objects.get(username='multi_state_user')
user.get_accessible_states()  # [<State: Delhi>, <State: UP>, <State: Rajasthan>]

# Sees data from all three states
user_data = StockistProductMatch.objects.filter(
    stockist__state__in=user.get_accessible_states()
)
```

## Data Import Best Practices

1. **First Import**: Use full import without `--incremental`
2. **Regular Updates**: Use `--incremental` flag to skip existing records
3. **Month-wise Import**: Use `--month-year` to import specific months
4. **Verify Data**: Check dashboard after import for statistics
5. **Review Mismatches**: Use mismatch report to identify data quality issues

## Performance Considerations

- Database indexes are created on frequently queried fields
- Pagination is used for large datasets (50-100 records per page)
- State filtering happens at database level for efficiency
- Use `select_related()` to reduce database queries

## Troubleshooting

### Import Errors
```bash
# Check CSV format
# Ensure all required columns are present
# Verify state names match existing states
```

### Access Denied
```bash
# Verify user has states assigned
user.get_accessible_states()

# Check user role
user.role  # Should be SUB_ADMIN or USER
```

### No Data Visible
```bash
# Ensure stockist's state matches user's assigned states
# Check if data was imported for the correct month
# Verify user is logged in
```

## Admin Interface

Register models in `admin.py`:

```python
from django.contrib import admin
from .models import Stockist, Division, Product, StockistProductMatch

@admin.register(Stockist)
class StockistAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'state', 'is_active']
    list_filter = ['state', 'is_active']
    search_fields = ['code', 'name']

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'division', 'is_active']
    list_filter = ['division', 'is_active']
    search_fields = ['code', 'name']

@admin.register(StockistProductMatch)
class StockistProductMatchAdmin(admin.ModelAdmin):
    list_display = ['stockist', 'month_year', 'validation', 'variance']
    list_filter = ['month_year', 'validation', 'stockist__state']
    search_fields = ['stockist__code', 'pdf_product', 'excel_product__name']
```

## Next Steps

1. Run migrations: `python manage.py migrate`
2. Prepare your CSV data file
3. Import data using management command
4. Add URL patterns to your project
5. Create templates for the views (optional, or use Django admin)
6. Test with different user roles and state assignments

## Support

For issues or questions, refer to:
- RBAC_README.md for role and permission details
- STATE_ACCESS_CONTROL_GUIDE.md for state-based filtering
- Django documentation for model and view customization
