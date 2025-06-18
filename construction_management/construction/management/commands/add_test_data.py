from django.core.management.base import BaseCommand
from construction.models import Project, NewLandExpense, NewManpowerExpense, NewMaterialExpense
from datetime import date

class Command(BaseCommand):
    help = 'Add test data to the database'

    def handle(self, *args, **options):
        # Create a test project
        project = Project.objects.create(
            name='Test Project',
            land_details='Test Land',
            land_address='Test Address',
            budget=1000000,
            status='Planned'
        )
        self.stdout.write(self.style.SUCCESS('Created test project'))

        # Create test expenses
        NewLandExpense.objects.create(
            project=project,
            date=date.today(),
            amount=100000,
            land_id='LAND001'
        )
        self.stdout.write(self.style.SUCCESS('Created land expense'))

        NewManpowerExpense.objects.create(
            project=project,
            date=date.today(),
            amount=50000,
            manpower_id='MAN001'
        )
        self.stdout.write(self.style.SUCCESS('Created manpower expense'))

        NewMaterialExpense.objects.create(
            project=project,
            date=date.today(),
            amount=75000,
            material_name='Cement'
        )
        self.stdout.write(self.style.SUCCESS('Created material expense')) 