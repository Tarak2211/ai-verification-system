"""
Script to prepare stockist data for import
This creates a CSV file from the provided data
"""
import csv

# Sample data structure based on your input
data = [
    {
        'Row Index': 62,
        'Stockist Code': 'KA0003',
        'state_name': 'KARNATAKA',
        'Stockist Name': 'MOHAN & CO.',
        'month_year': 'Oct-2025',
        'PDF Division': 'AESTHETIC',
        'Excel Division': 'AESTHETIC',
        'PDF Product': 'DERMADEW GLOW CREAM 50GM',
        'Product Code': 'PR022',
        'Excel Product': 'DERMADEW GLOW CREAM 50GM',
        'Match Method': 'Exact',
        'PDF Closing': 46,
        'Excel Closing': 46,
        'Variance': 0,
        'Validation': 'MATCHED',
        'Label': 'Matched',
        'Description': 'Product matched perfectly with zero variance'
    },
    # Add more sample records here
]

def create_csv(filename='stockist_data.csv'):
    """Create CSV file from data"""
    
    fieldnames = [
        'Row Index', 'Stockist Code', 'state_name', 'Stockist Name',
        'month_year', 'PDF Division', 'Excel Division', 'PDF Product',
        'Product Code', 'Excel Product', 'Match Method', 'PDF Closing',
        'Excel Closing', 'Variance', 'Validation', 'Label', 'Description'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"CSV file created: {filename}")
    print(f"Total records: {len(data)}")

if __name__ == '__main__':
    create_csv()
