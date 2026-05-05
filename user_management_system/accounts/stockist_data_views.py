"""
Stockist Data Views - Detailed data table with filters
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import StockistProductMatch, Division, Stockist


@login_required
def stockist_data_table(request):
    """
    Display detailed stockist product matching data with filters
    Shows all columns in a comprehensive table format
    """
    user = request.user
    
    # Get user's accessible states
    accessible_states = user.get_accessible_states()
    
    # Base queryset filtered by user's states
    if user.is_superuser or user.is_super_admin():
        matches = StockistProductMatch.objects.all()
    else:
        matches = StockistProductMatch.objects.filter(
            stockist__state__in=accessible_states
        )
    
    # Get filter parameters
    month_year = request.GET.get('month_year', '')
    validation = request.GET.get('validation', '')
    division = request.GET.get('division', '')
    stockist_code = request.GET.get('stockist_code', '')
    state_id = request.GET.get('state', '')
    search = request.GET.get('search', '')
    
    # Apply filters
    if month_year:
        matches = matches.filter(month_year=month_year)
    
    if validation:
        matches = matches.filter(validation=validation)
    
    if division:
        matches = matches.filter(excel_division__name=division)
    
    if stockist_code:
        matches = matches.filter(stockist__code__icontains=stockist_code)
    
    if state_id:
        matches = matches.filter(stockist__state_id=state_id)
    
    if search:
        matches = matches.filter(
            Q(pdf_product__icontains=search) |
            Q(excel_product__name__icontains=search) |
            Q(stockist__name__icontains=search)
        )
    
    # Order by month, stockist, and row index
    matches = matches.select_related(
        'stockist', 'stockist__state', 'excel_division', 'excel_product'
    ).order_by('-month_year', 'stockist__code', 'row_index')
    
    # Get available filter options (based on user's access)
    if user.is_superuser or user.is_super_admin():
        available_months = StockistProductMatch.objects.values_list(
            'month_year', flat=True
        ).distinct().order_by('-month_year')
        available_divisions = Division.objects.all().order_by('name')
        available_stockists = Stockist.objects.all().order_by('code')
    else:
        available_months = StockistProductMatch.objects.filter(
            stockist__state__in=accessible_states
        ).values_list('month_year', flat=True).distinct().order_by('-month_year')
        available_divisions = Division.objects.filter(
            products__stockistproductmatch__stockist__state__in=accessible_states
        ).distinct().order_by('name')
        available_stockists = Stockist.objects.filter(
            state__in=accessible_states
        ).order_by('code')
    
    # Pagination
    paginator = Paginator(matches, 50)  # 50 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_records': matches.count(),
        'matched': matches.filter(validation='MATCHED').count(),
        'mismatched': matches.exclude(validation='MATCHED').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'available_months': available_months,
        'available_divisions': available_divisions,
        'available_stockists': available_stockists,
        'selected_month': month_year,
        'selected_validation': validation,
        'selected_division': division,
        'selected_stockist': stockist_code,
        'selected_state': state_id,
        'search_query': search,
        'user_states': accessible_states,
    }
    
    return render(request, 'accounts/stockist_data_table.html', context)
