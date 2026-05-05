"""
Management command to load sample stockist data directly
This is useful for testing without needing a CSV file
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import State, Stockist, Division, Product, StockistProductMatch


class Command(BaseCommand):
    help = 'Load sample stockist product matching data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading sample stockist data...')
        
        stats = {
            'states': 0,
            'stockists': 0,
            'divisions': 0,
            'products': 0,
            'matches': 0,
        }
        
        try:
            with transaction.atomic():
                # Sample data
                sample_data = [
                    {
                        'row_index': 62,
                        'stockist_code': 'KA0003',
                        'state_name': 'Karnataka',
                        'stockist_name': 'MOHAN & CO.',
                        'month_year': 'Oct-2025',
                        'pdf_division': 'AESTHETIC',
                        'excel_division': 'AESTHETIC',
                        'pdf_product': 'DERMADEW GLOW CREAM 50GM',
                        'product_code': 'PR022',
                        'excel_product': 'DERMADEW GLOW CREAM 50GM',
                        'match_method': 'EXACT',
                        'pdf_closing': 46,
                        'excel_closing': 46,
                        'variance': 0,
                        'validation': 'MATCHED',
                        'label': 'Matched',
                        'description': 'Product matched perfectly with zero variance'
                    },
                    {
                        'row_index': 71,
                        'stockist_code': 'KA0003',
                        'state_name': 'Karnataka',
                        'stockist_name': 'MOHAN & CO.',
                        'month_year': 'Oct-2025',
                        'pdf_division': 'AESTHETIC',
                        'excel_division': 'AESTHETIC',
                        'pdf_product': 'DERMADEW GLOW FACE WASH 100ML',
                        'product_code': 'PR208',
                        'excel_product': 'DERMADEW GLOW FACE WASH 100ML',
                        'match_method': 'EXACT',
                        'pdf_closing': 0,
                        'excel_closing': 0,
                        'variance': 0,
                        'validation': 'MATCHED',
                        'label': 'Matched',
                        'description': 'Product matched perfectly with zero variance'
                    },
                    {
                        'row_index': 0,
                        'stockist_code': 'KA0003',
                        'state_name': 'Karnataka',
                        'stockist_name': 'MOHAN & CO.',
                        'month_year': 'Oct-2025',
                        'pdf_division': 'AESTHETIC',
                        'excel_division': '',
                        'pdf_product': 'MX F 5% 60ML',
                        'product_code': '',
                        'excel_product': '',
                        'match_method': '',
                        'pdf_closing': 0,
                        'excel_closing': 0,
                        'variance': 0,
                        'validation': 'PRODUCT_NOT_FOUND',
                        'label': 'Product Not Found',
                        'description': 'Product does not exist in Excel master file'
                    },
                    {
                        'row_index': 95,
                        'stockist_code': 'KA0004',
                        'state_name': 'Karnataka',
                        'stockist_name': 'RSM PHARMA PVT LTD',
                        'month_year': 'Oct-2025',
                        'pdf_division': 'AESTHETIC',
                        'excel_division': 'AESTHETIC',
                        'pdf_product': 'AQUAHANCE ADVANCED NIGHT REPAIR SERUM',
                        'product_code': 'PR259',
                        'excel_product': 'AQUAHANCE ADVANCED NIGHT REPAIR SERUM 25ML',
                        'match_method': 'FUZZY',
                        'pdf_closing': 23,
                        'excel_closing': 23,
                        'variance': 0,
                        'validation': 'MATCHED',
                        'label': 'Matched',
                        'description': 'Product matched perfectly with zero variance'
                    },
                    {
                        'row_index': 100,
                        'stockist_code': 'KA0004',
                        'state_name': 'Karnataka',
                        'stockist_name': 'RSM PHARMA PVT LTD',
                        'month_year': 'Oct-2025',
                        'pdf_division': 'AESTHETIC',
                        'excel_division': 'AESTHETIC',
                        'pdf_product': 'GTHANCE 500MG TABLETS',
                        'product_code': 'PR268',
                        'excel_product': 'CUTIHANCE MEN TABLETS',
                        'match_method': 'FUZZY',
                        'pdf_closing': 40,
                        'excel_closing': 27,
                        'variance': 13,
                        'validation': 'QUANTITY_MISMATCH',
                        'label': 'Quantity Mismatch',
                        'description': 'Product matched but closing quantity differs between PDF and Excel'
                    },
                ]
                
                # Process each record
                for record in sample_data:
                    # Get or create state
                    state, created = State.objects.get_or_create(
                        name=record['state_name'],
                        defaults={'code': record['state_name'][:3].upper(), 'is_active': True}
                    )
                    if created:
                        stats['states'] += 1
                    
                    # Get or create stockist
                    stockist, created = Stockist.objects.get_or_create(
                        code=record['stockist_code'],
                        defaults={'name': record['stockist_name'], 'state': state}
                    )
                    if created:
                        stats['stockists'] += 1
                    
                    # Get or create division
                    excel_division = None
                    if record['excel_division']:
                        excel_division, created = Division.objects.get_or_create(
                            name=record['excel_division'],
                            defaults={'is_active': True}
                        )
                        if created:
                            stats['divisions'] += 1
                    
                    # Get or create product
                    excel_product = None
                    if record['product_code'] and record['excel_product'] and excel_division:
                        excel_product, created = Product.objects.get_or_create(
                            code=record['product_code'],
                            defaults={
                                'name': record['excel_product'],
                                'division': excel_division,
                                'is_active': True
                            }
                        )
                        if created:
                            stats['products'] += 1
                    
                    # Create match record
                    match_record, created = StockistProductMatch.objects.update_or_create(
                        stockist=stockist,
                        month_year=record['month_year'],
                        row_index=record['row_index'],
                        defaults={
                            'pdf_division': record['pdf_division'],
                            'pdf_product': record['pdf_product'],
                            'pdf_closing': record['pdf_closing'],
                            'excel_division': excel_division,
                            'excel_product': excel_product,
                            'excel_closing': record['excel_closing'],
                            'match_method': record['match_method'],
                            'variance': record['variance'],
                            'validation': record['validation'],
                            'label': record['label'],
                            'description': record['description'],
                        }
                    )
                    if created:
                        stats['matches'] += 1
                
                # Print summary
                self.stdout.write(self.style.SUCCESS('\n=== Load Summary ==='))
                self.stdout.write(f"States created: {stats['states']}")
                self.stdout.write(f"Stockists created: {stats['stockists']}")
                self.stdout.write(f"Divisions created: {stats['divisions']}")
                self.stdout.write(f"Products created: {stats['products']}")
                self.stdout.write(self.style.SUCCESS(f"Match records created: {stats['matches']}"))
                
                self.stdout.write(self.style.SUCCESS('\nSample data loaded successfully!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise
