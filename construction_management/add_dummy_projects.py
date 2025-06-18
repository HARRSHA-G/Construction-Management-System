import os
import django
from decimal import Decimal
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_management.settings')
django.setup()

from construction.models import Project

# Dummy project data
dummy_projects = [
    {
        'name': 'Luxury Villa Complex',
        'land_details': '5000 sq ft plot with garden area',
        'land_address': '123 Palm Avenue, Green Valley, Hyderabad',
        'budget': Decimal('25000000.00'),
        'duration_months': 18,
        'status': 'Active',
        'total_paid': Decimal('5000000.00')
    },
    {
        'name': 'Commercial Plaza',
        'land_details': '10000 sq ft commercial plot',
        'land_address': '456 Business Park, Tech City, Bangalore',
        'budget': Decimal('50000000.00'),
        'duration_months': 24,
        'status': 'Active',
        'total_paid': Decimal('15000000.00')
    },
    {
        'name': 'Residential Apartments',
        'land_details': '20000 sq ft residential plot',
        'land_address': '789 Skyline Heights, Mumbai',
        'budget': Decimal('75000000.00'),
        'duration_months': 30,
        'status': 'On Hold',
        'total_paid': Decimal('20000000.00')
    },
    {
        'name': 'Shopping Mall',
        'land_details': '30000 sq ft commercial plot',
        'land_address': '321 Retail Hub, Delhi',
        'budget': Decimal('100000000.00'),
        'duration_months': 36,
        'status': 'Active',
        'total_paid': Decimal('30000000.00')
    },
    {
        'name': 'Office Complex',
        'land_details': '15000 sq ft commercial plot',
        'land_address': '654 Corporate Park, Chennai',
        'budget': Decimal('40000000.00'),
        'duration_months': 20,
        'status': 'Completed',
        'total_paid': Decimal('40000000.00')
    },
    {
        'name': 'Gated Community',
        'land_details': '50000 sq ft residential plot',
        'land_address': '987 Green Meadows, Pune',
        'budget': Decimal('150000000.00'),
        'duration_months': 42,
        'status': 'Active',
        'total_paid': Decimal('45000000.00')
    },
    {
        'name': 'Hotel Project',
        'land_details': '25000 sq ft commercial plot',
        'land_address': '147 Hospitality Lane, Goa',
        'budget': Decimal('80000000.00'),
        'duration_months': 28,
        'status': 'Active',
        'total_paid': Decimal('25000000.00')
    },
    {
        'name': 'Industrial Warehouse',
        'land_details': '40000 sq ft industrial plot',
        'land_address': '258 Industrial Zone, Ahmedabad',
        'budget': Decimal('60000000.00'),
        'duration_months': 16,
        'status': 'Completed',
        'total_paid': Decimal('60000000.00')
    },
    {
        'name': 'Educational Campus',
        'land_details': '35000 sq ft institutional plot',
        'land_address': '369 Education Hub, Kolkata',
        'budget': Decimal('90000000.00'),
        'duration_months': 32,
        'status': 'Active',
        'total_paid': Decimal('35000000.00')
    },
    {
        'name': 'Healthcare Center',
        'land_details': '20000 sq ft institutional plot',
        'land_address': '741 Medical District, Kochi',
        'budget': Decimal('55000000.00'),
        'duration_months': 22,
        'status': 'On Hold',
        'total_paid': Decimal('18000000.00')
    }
]

def add_dummy_projects():
    print("Adding dummy projects...")
    for project_data in dummy_projects:
        try:
            project = Project.objects.create(**project_data)
            print(f"Created project: {project.name} (ID: {project.project_id})")
        except Exception as e:
            print(f"Error creating project {project_data['name']}: {str(e)}")
    print("Finished adding dummy projects!")

if __name__ == '__main__':
    add_dummy_projects() 