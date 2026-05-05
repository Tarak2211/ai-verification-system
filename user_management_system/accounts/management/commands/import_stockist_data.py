"""
Management command to import stockist product matching data
Supports incremental loading and CSV/Excel input
"""
import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import State
from accounts.stockist_models import Stockist, Division, Product, StockistProductMatch


class Command(BaseCommand):
    help = 'Import stockist product matching data from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument(
            '--incremental',
            action='store_true',
            help='Only insert new records (skip existing)',
        )
        parser.add_argument(
            '--month-year',
            type=str,
            help='Filter by specific month-year (e.g., Oct-2025)',
        )
    
    def handle(self, *args, **options):
        csv_file = options['csv_file']
        incremental = options['incremental']
        filter_month = options.get('month_year')
        
        self.stdout.write(f'Reading data from: {csv_file}')
        
        stats = {
            'total': 0,
            'created': 0,
            'skipped': 0,
            'errors': 0,
        }
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                with transaction.atomic():
                    for row in reader:
                        stats['total'] += 1
                        
                        # Filter by month if specified
                        if filter_month and row.get('month_year') != filter_month:
                            stats['skipped'] += 1
                            continue
                        
                        try:
                            result = self.process_row(row, incremental)
                            if result == 'created':
                                stats['created'] += 1
                            elif result == 'skipped':
                                stats['skipped'] += 1
                        except Exception as e:
                            stats['errors'] += 1
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Error processing row {stats['total']}: {str(e)}"
                                )
                            )
            
            # Print summary
            self.stdout.write(self.style.SUCCESS('\n=== Import Summary ==='))
            self.stdout.write(f"Total rows processed: {stats['total']}")
            self.stdout.write(self.style.SUCCESS(f"Created: {stats['created']}"))
            self.stdout.write(self.style.WARNING(f"Skipped: {stats['skipped']}"))
            if stats['errors'] > 0:
                self.stdout.write(self.style.ERROR(f"Errors: {stats['errors']}"))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def process_row(self, row, incremental):
        """Process a single row of data"""
        
        # Get or create state
        state_name = row.get('state_name', '').strip()
        if not state_name:
            raise ValueError('state_name is required')
        
        state, _ = State.objects.get_or_create(
            name=state_name,
            defaults={'code': state_name[:3].upper(), 'is_active': True}
        )
        
        # Get or create stockist
        stockist_code = row.get('Stockist Code', '').strip()
        stockist_name = row.get('Stockist Name', '').strip()
        
        if not stockist_code:
            raise ValueError('Stockist Code is required')
        
        stockist, _ = Stockist.objects.get_or_create(
            code=stockist_code,
            defaults={'name': stockist_name, 'state': state}
        )
        
        # Get month_year and row_index
        month_year = row.get('month_year', '').strip()
        row_index = int(row.get('Row Index', 0))
        
        # Check if record exists (for incremental load)
        if incremental:
            exists = StockistProductMatch.objects.filter(
                stockist=stockist,
                month_year=month_year,
                row_index=row_index
            ).exists()
            
            if exists:
                return 'skipped'
        
        # Get or create divisions
        excel_division_name = row.get('Excel Division', '').strip()
        excel_division = None
        if excel_division_name:
            excel_division, _ = Division.objects.get_or_create(
                name=excel_division_name,
                defaults={'is_active': True}
            )
        
        # Get or create product
        product_code = row.get('Product Code', '').strip()
        excel_product_name = row.get('Excel Product', '').strip()
        excel_product = None
        
        if product_code and excel_product_name and excel_division:
            excel_product, _ = Product.objects.get_or_create(
                code=product_code,
                defaults={
                    'name': excel_product_name,
                    'division': excel_division,
                    'is_active': True
                }
            )
        
        # Create or update match record
        match_record, created = StockistProductMatch.objects.update_or_create(
            stockist=stockist,
            month_year=month_year,
            row_index=row_index,
            defaults={
                'pdf_division': row.get('PDF Division', '').strip(),
                'pdf_product': row.get('PDF Product', '').strip(),
                'pdf_closing': int(row.get('PDF Closing', 0) or 0),
                'excel_division': excel_division,
                'excel_product': excel_product,
                'excel_closing': int(row.get('Excel Closing', 0) or 0),
                'match_method': row.get('Match Method', '').strip(),
                'variance': int(row.get('Variance', 0) or 0),
                'validation': row.get('Validation', '').strip(),
                'label': row.get('Label', '').strip(),
                'description': row.get('Description', '').strip(),
            }
        )
        
        return 'created' if created else 'skipped'
