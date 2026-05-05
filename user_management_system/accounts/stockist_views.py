"""
Views for stockist product matching data
Implements state-based access control using existing RBAC system
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from .models import CustomUser, Stockist, StockistProductMatch, Division


@login_required
def stockist_dashboard(request):
    """Dashboard showing stockist data summary with state filtering"""
    user = request.user
    
    # Get user's accessible states
    accessible_states = user.get_accessible_states()
    
    # Base queryset filtered by user's states
    if user.is_superuser:
        matches_qs = StockistProductMatch.objects.all()
    else:
        matches_qs = StockistProductMatch.objects.filter(
            stockist__state__in=accessible_states
        )
    
    # Get filter parameters
    month_year = request.GET.get('month_year', '')
    validation = request.GET.get('validation', '')
    division = request.GET.get('division', '')
    
    # Apply filters
    if month_year:
        matches_qs = matches_qs.filter(month_year=month_year)
    if validation:
        matches_qs = matches_qs.filter(validation=validation)
    if division:
        matches_qs = matches_qs.filter(excel_division__name=division)
    
    # Get statistics
    stats = {
        'total_records': matches_qs.count(),
        'matched': matches_qs.filter(validation='MATCHED').count(),
        'quantity_mismatch': matches_qs.filter(validation='QUANTITY_MISMATCH').count(),
        'division_mismatch': matches_qs.filter(validation='DIVISION_MISMATCH').count(),
        'product_not_found': matches_qs.filter(validation='PRODUCT_NOT_FOUND').count(),
        'total_variance': matches_qs.aggregate(Sum('variance'))['variance__sum'] or 0,
    }
    
    # Get available filters
    available_months = StockistProductMatch.objects.filter(
        stockist__state__in=accessible_states
    ).values_list('month_year', flat=True).distinct().order_by('-month_year')
    
    available_divisions = Division.objects.filter(
        products__stockistproductmatch__stockist__state__in=accessible_states
    ).distinct().order_by('name')
    
    context = {
        'stats': stats,
        'available_months': available_months,
        'available_divisions': available_divisions,
        'selected_month': month_year,
        'selected_validation': validation,
        'selected_division': division,
        'user_states': accessible_states,
    }
    
    return render(request, 'accounts/stockist_dashboard.html', context)


@login_required
def stockist_list(request):
    """List all stockists accessible to the user"""
    user = request.user
    
    # Get user's accessible states
    accessible_states = user.get_accessible_states()
    
    # Filter stockists by user's states
    if user.is_superuser:
        stockists = Stockist.objects.all()
    else:
        stockists = Stockist.objects.filter(state__in=accessible_states)
    
    stockists = stockists.select_related('state').order_by('code')
    
    # Pagination
    paginator = Paginator(stockists, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_stockists': stockists.count(),
    }
    
    return render(request, 'accounts/stockist_list.html', context)


@login_required
def stockist_detail(request, stockist_code):
    """View detailed product matching data for a specific stockist"""
    user = request.user
    
    # Get user's accessible states
    accessible_states = user.get_accessible_states()
    
    # Get stockist with state check
    if user.is_superuser:
        stockist = get_object_or_404(Stockist, code=stockist_code)
    else:
        stockist = get_object_or_404(
            Stockist,
            code=stockist_code,
            state__in=accessible_states
        )
    
    # Get filter parameters
    month_year = request.GET.get('month_year', '')
    validation = request.GET.get('validation', '')
    
    # Get product matches
    matches = stockist.product_matches.select_related(
        'excel_division', 'excel_product'
    ).order_by('-month_year', 'row_index')
    
    if month_year:
        matches = matches.filter(month_year=month_year)
    if validation:
        matches = matches.filter(validation=validation)
    
    # Pagination
    paginator = Paginator(matches, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available months for this stockist
    available_months = stockist.product_matches.values_list(
        'month_year', flat=True
    ).distinct().order_by('-month_year')
    
    context = {
        'stockist': stockist,
        'page_obj': page_obj,
        'available_months': available_months,
        'selected_month': month_year,
        'selected_validation': validation,
        'total_matches': matches.count(),
    }
    
    return render(request, 'accounts/stockist_detail.html', context)


@login_required
def product_mismatch_report(request):
    """Report showing all mismatches for review"""
    user = request.user
    
    # Get user's accessible states
    accessible_states = user.get_accessible_states()
    
    # Get mismatches only
    if user.is_superuser:
        mismatches = StockistProductMatch.objects.exclude(validation='MATCHED')
    else:
        mismatches = StockistProductMatch.objects.filter(
            stockist__state__in=accessible_states
        ).exclude(validation='MATCHED')
    
    # Get filter parameters
    month_year = request.GET.get('month_year', '')
    validation = request.GET.get('validation', '')
    
    if month_year:
        mismatches = mismatches.filter(month_year=month_year)
    if validation:
        mismatches = mismatches.filter(validation=validation)
    
    mismatches = mismatches.select_related(
        'stockist', 'stockist__state', 'excel_division', 'excel_product'
    ).order_by('-month_year', 'stockist__code', 'row_index')
    
    # Pagination
    paginator = Paginator(mismatches, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics by validation type
    validation_stats = {}
    for choice in StockistProductMatch.VALIDATION_CHOICES:
        if choice[0] != 'MATCHED':
            count = mismatches.filter(validation=choice[0]).count()
            validation_stats[choice[1]] = count
    
    context = {
        'page_obj': page_obj,
        'validation_stats': validation_stats,
        'selected_month': month_year,
        'selected_validation': validation,
        'total_mismatches': mismatches.count(),
    }
    
    return render(request, 'accounts/product_mismatch_report.html', context)
