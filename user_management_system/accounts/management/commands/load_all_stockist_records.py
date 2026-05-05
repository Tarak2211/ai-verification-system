"""
Management command to load all stockist product matching records
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import State, Stockist, Division, Product, StockistProductMatch


class Command(BaseCommand):
    help = 'Load all stockist product matching records with diverse states'
    
    def handle(self, *args, **options):
        self.stdout.write('Loading all stockist product matching records...')
        
        # Define all records with complete data
        records = []
        
        # KA0003 - Karnataka
        ka0003_records = [
            (62, 'DERMADEW GLOW CREAM 50GM', 'PR022', 'DERMADEW GLOW CREAM 50GM', 'EXACT', 46, 46),
            (71, 'DERMADEW GLOW FACE WASH 100ML', 'PR208', 'DERMADEW GLOW FACE WASH 100ML', 'EXACT', 0, 0),
            (63, 'DERMADEW LITE SOAP 75GM', 'PR023', 'DERMADEW LITE SOAP 75GM', 'EXACT', 53, 53),
            (64, 'HHLITE CREAM 20GM', 'PR055', 'HHLITE CREAM 20GM', 'EXACT', 13, 13),
            (65, 'MX 10 TOPICAL SOLUTION 60ML', 'PR082', 'MX-10 TOPICAL SOLUTION 60ML', 'EXACT', 22, 22),
            (66, 'MX 2 TOPICAL SOLUTION 60ML', 'PR083', 'MX-2 TOPICAL SOLUTION 60ML', 'EXACT', 8, 8),
            (67, 'MX 5 TOPICAL SOLUTION 60ML', 'PR084', 'MX-5 TOPICAL SOLUTION 60ML', 'EXACT', 0, 0),
        ]
        
        for row_idx, pdf_prod, prod_code, excel_prod, match_method, pdf_close, excel_close in ka0003_records:
            records.append({
                'stockist_code': 'KA0003',
                'row_index': row_idx,
                'pdf_product': pdf_prod,
                'product_code': prod_code,
                'excel_product': excel_prod,
                'match_method': match_method,
                'pdf_closing': pdf_close,
                'excel_closing': excel_close,
            })
        
        # KA0004 - Maharashtra  
        ka0004_records = [
            (95, 'AQUAHANCE ADVANCED NIGHT REPAIR SERUM', 'PR259', 'AQUAHANCE ADVANCED NIGHT REPAIR SERUM 25ML', 'FUZZY', 23, 23),
            (98, 'AQUAHANCE HAIR REVITALIZING CONDITIONER', 'PR262', 'AQUAHANCE HAIR REVITALIZING CONDITIONER 150GM', 'FUZZY', 7, 7),
            (96, 'AQUAHANCE MOISTURE SURGE FACE WASH', 'PR260', 'AQUAHANCE MOISTURE SURGE FACE WASH 100ML', 'FUZZY', 186, 186),
            (97, 'AQUAHANCE MOISTURE SURGE GEL', 'PR261', 'AQUAHANCE MOISTURE SURGE GEL 45GM', 'FUZZY', 26, 26),
            (99, 'AQUAHANCE MOISTURE SURGE SOAP', 'PR265', 'AQUAHANCE MOISTURE SURGE SOAP 125GM', 'FUZZY', 67, 67),
            (101, 'CUTIHANCE WOMEN TABLETS', 'PR269', 'CUTIHANCE WOMEN TABLETS', 'EXACT', 12, 12),
            (93, 'DERMADEW AHF SHAMPOO', 'PR242', 'DERMADEW AHF SHAMPOO 80ML', 'FUZZY', 512, 512),
            (82, 'DERMADEW GLOW CREAM', 'PR022', 'DERMADEW GLOW CREAM 50GM', 'FUZZY', 73, 73),
            (91, 'DERMADEW GLOW FACE WASH', 'PR208', 'DERMADEW GLOW FACE WASH 100ML', 'FUZZY', 77, 77),
            (94, 'DERMADEW HAIR SERUM', 'PR250', 'DERMADEW HAIR SERUM 60ML', 'FUZZY', 21, 21),
            (83, 'DERMADEW LITE SOAP', 'PR023', 'DERMADEW LITE SOAP 75GM', 'FUZZY', 633, 633),
            (84, 'HHLITE CREAM 20GM', 'PR055', 'HHLITE CREAM 20GM', 'EXACT', 409, 409),
            (85, 'MX 10 TOPICAL SOLUTION', 'PR082', 'MX-10 TOPICAL SOLUTION 60ML', 'FUZZY', 62, 62),
            (86, 'MX 2 TOPICAL SOLUTION', 'PR083', 'MX-2 TOPICAL SOLUTION 60ML', 'FUZZY', 17, 17),
            (87, 'MX 5 TOPICAL SOLUTION', 'PR084', 'MX-5 TOPICAL SOLUTION 60ML', 'FUZZY', 99, 99),
            (89, 'MX F 5% TOPICAL SOLUTION', 'PR177', 'MX-F 5% TOPICAL SOLUTION 60ML', 'FUZZY', 45, 45),
            (88, 'SUNBAN MATTE GEL', 'PR099', 'SUNBAN MATTE GEL 75GM', 'FUZZY', 70, 70),
            (90, 'SUNBAN SOFT GEL', 'PR178', 'SUNBAN SOFT 75GM', 'FUZZY', 45, 45),
        ]
        
        for row_idx, pdf_prod, prod_code, excel_prod, match_method, pdf_close, excel_close in ka0004_records:
            records.append({
                'stockist_code': 'KA0004',
                'row_index': row_idx,
                'pdf_product': pdf_prod,
                'product_code': prod_code,
                'excel_product': excel_prod,
                'match_method': match_method,
                'pdf_closing': pdf_close,
                'excel_closing': excel_close,
            })
        
        # KA0007 - Tamil Nadu
        ka0007_records = [
            (16, 'AQUAHANCE MOISTURE 100ML', 'PR260', 'AQUAHANCE MOISTURE SURGE FACE WASH 100ML', 'FUZZY', 34, 34),
            (3, 'DERMADEW LITE SOAP 75GM', 'PR023', 'DERMADEW LITE SOAP 75GM', 'EXACT', 24, 24),
            (13, 'DERMADEW AHF SHAMPC80ML', 'PR242', 'DERMADEW AHF SHAMPOO 80ML', 'FUZZY', 48, 48),
            (2, 'DERMADEW GLOW CREA 50GM', 'PR022', 'DERMADEW GLOW CREAM 50GM', 'FUZZY', 0, 0),
            (14, 'DERMADEW HAIR SERUM 60ML', 'PR250', 'DERMADEW HAIR SERUM 60ML', 'EXACT', 17, 17),
            (4, 'HHLITE CREAM 20GM', 'PR055', 'HHLITE CREAM 20GM', 'EXACT', 39, 39),
            (5, 'MX 10 TOPICAL SOLUTION 60ML', 'PR082', 'MX-10 TOPICAL SOLUTION 60ML', 'EXACT', 0, 0),
            (9, 'MX F 5% LOTION 60ML', 'PR177', 'MX-F 5% TOPICAL SOLUTION 60ML', 'FUZZY', 23, 23),
            (6, 'MX-2 SOLUTION 60ML', 'PR083', 'MX-2 TOPICAL SOLUTION 60ML', 'FUZZY', 3, 3),
            (7, 'MX-5 SOLUTION 60ML', 'PR084', 'MX-5 TOPICAL SOLUTION 60ML', 'FUZZY', 0, 0),
            (10, 'SUNBAN SOFT GEL 75GM', 'PR178', 'SUNBAN SOFT 75GM', 'FUZZY', 46, 46),
            (8, 'SUNBAN MATTE GEL 75GM 75GM', 'PR099', 'SUNBAN MATTE GEL 75GM', 'FUZZY', 51, 51),
        ]
        
        for row_idx, pdf_prod, prod_code, excel_prod, match_method, pdf_close, excel_close in ka0007_records:
            records.append({
                'stockist_code': 'KA0007',
                'row_index': row_idx,
                'pdf_product': pdf_prod,
                'product_code': prod_code,
                'excel_product': excel_prod,
                'match_method': match_method,
                'pdf_closing': pdf_close,
                'excel_closing': excel_close,
            })
        
        # KA0008 - Gujarat
        ka0008_records = [
            (23, 'DERMADEW LITE SOAP 75GM', 'PR023', 'DERMADEW LITE SOAP 75GM', 'EXACT', 48, 48),
            (24, 'HHLITE CREAM 20GM', 'PR055', 'HHLITE CREAM 20GM', 'EXACT', 0, 0),
            (26, 'MX-2 TOPICAL SOLUTION 60ML', 'PR083', 'MX-2 TOPICAL SOLUTION 60ML', 'EXACT', 0, 0),
            (27, 'MX-5 TOPICAL SOLUTION 60ML', 'PR084', 'MX-5 TOPICAL SOLUTION 60ML', 'EXACT', 0, 0),
            (28, 'SUNBAN MATTE GEL 75GM', 'PR099', 'SUNBAN MATTE GEL 75GM', 'EXACT', 0, 0),
        ]
        
        for row_idx, pdf_prod, prod_code, excel_prod, match_method, pdf_close, excel_close in ka0008_records:
            records.append({
                'stockist_code': 'KA0008',
                'row_index': row_idx,
                'pdf_product': pdf_prod,
                'product_code': prod_code,
                'excel_product': excel_prod,
                'match_method': match_method,
                'pdf_closing': pdf_close,
                'excel_closing': excel_close,
            })
        
        # KA0011 - Delhi
        ka0011_records = [
            (115, 'AQUAHANCE ADVANCED.NIGHT REPAIR 25M', 'PR259', 'AQUAHANCE ADVANCED NIGHT REPAIR SERUM 25ML', 'FUZZY', 28, 28),
            (119, 'AQUAHANCE MOISTURE SURGE SOAP 1', 'PR265', 'AQUAHANCE MOISTURE SURGE SOAP 125GM', 'FUZZY', 6, 6),
            (116, 'AQUAHANCE MOISTURE.SURGE FACE 10', 'PR260', 'AQUAHANCE MOISTURE SURGE FACE WASH 100ML', 'FUZZY', 68, 68),
            (117, 'AQUAHANCE MOISTURE.SURGE GEL 450', 'PR261', 'AQUAHANCE MOISTURE SURGE GEL 45GM', 'FUZZY', 48, 48),
        ]
        
        for row_idx, pdf_prod, prod_code, excel_prod, match_method, pdf_close, excel_close in ka0011_records:
            records.append({
                'stockist_code': 'KA0011',
                'row_index': row_idx,
                'pdf_product': pdf_prod,
                'product_code': prod_code,
                'excel_product': excel_prod,
                'match_method': match_method,
                'pdf_closing': pdf_close,
                'excel_closing': excel_close,
            })
        
        self.stdout.write(f'Total records to load: {len(records)}')
        
        # Load data
        stats = {'created': 0, 'updated': 0, 'errors': 0}
        
        with transaction.atomic():
            division = Division.objects.get(name='AESTHETIC')
            
            for rec in records:
                try:
                    stockist = Stockist.objects.get(code=rec['stockist_code'])
                    product = Product.objects.get(code=rec['product_code'])
                    
                    variance = rec['pdf_closing'] - rec['excel_closing']
                    if variance == 0:
                        validation = 'MATCHED'
                        label = 'Matched'
                        description = 'Product matched perfectly with zero variance'
                    else:
                        validation = 'QUANTITY_MISMATCH'
                        label = 'Quantity Mismatch'
                        description = 'Product matched but closing quantity differs between PDF and Excel'
                    
                    obj, created = StockistProductMatch.objects.update_or_create(
                        stockist=stockist,
                        month_year='Oct-2025',
                        row_index=rec['row_index'],
                        defaults={
                            'pdf_division': 'AESTHETIC',
                            'pdf_product': rec['pdf_product'],
                            'pdf_closing': rec['pdf_closing'],
                            'excel_division': division,
                            'excel_product': product,
                            'excel_closing': rec['excel_closing'],
                            'match_method': rec['match_method'],
                            'variance': variance,
                            'validation': validation,
                            'label': label,
                            'description': description,
                        }
                    )
                    
                    if created:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error with row {rec["row_index"]}: {str(e)}'))
                    stats['errors'] += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(f'Created: {stats["created"]}')
        self.stdout.write(f'Updated: {stats["updated"]}')
        self.stdout.write(f'Errors: {stats["errors"]}')
        self.stdout.write(f'Total records in database: {StockistProductMatch.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\n✅ Data loading complete!'))
