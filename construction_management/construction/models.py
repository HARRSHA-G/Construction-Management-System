from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
import random
import string
from django.db.models import Sum

class LaborWorkType(models.Model):
    WORK_TYPES = [
        ('construction', 'Construction work'),
        ('water_sanitary', 'Water and sanitary'),
        ('electric', 'Electric'),
        ('granite', 'Granite'),
        ('wood_work', 'Wood work'),
        ('grill_work', 'Grill work'),
        ('paint_work', 'Paint work'),
        ('earth_work', 'Earth work'),
        ('carpenter', 'Carpenter'),
    ]

    name = models.CharField(max_length=50, choices=WORK_TYPES, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        ordering = ['name']

class Project(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Cancelled', 'Cancelled')
    ]

    project_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    land_details = models.TextField()
    land_address = models.TextField()
    budget = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    duration_months = models.PositiveIntegerField(default=1, help_text="Project duration in months")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active')
    total_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_id} - {self.name}"

    def clean(self):
        if self.total_paid > self.budget:
            raise ValidationError({'total_paid': 'Total paid amount cannot exceed budget'})
        if self.remaining_amount < 0:
            raise ValidationError({'remaining_amount': 'Remaining amount cannot be negative'})

    def save(self, *args, **kwargs):
        # Only auto-generate project_id for new projects
        if not self.pk and not self.project_id:  # Check if this is a new project
            # Get the last project ID
            last_project = Project.objects.exclude(project_id='ID-0000').order_by('-project_id').first()
            if last_project:
                # Extract the number from the last project ID and increment
                last_id = last_project.project_id[3:]  # Get part after 'ID-'
                try:
                    # Try to parse as number first
                    last_number = int(last_id)
                    new_number = last_number + 1
                    self.project_id = f"ID-{new_number:04d}"
                except ValueError:
                    # If not a number, generate a new alphanumeric ID
                    chars = string.ascii_uppercase + string.digits
                    new_id = ''.join(random.choices(chars, k=4))
                    self.project_id = f"ID-{new_id}"
            else:
                self.project_id = "ID-0001"
        
        # Calculate remaining amount before saving
        self.remaining_amount = self.budget - self.total_paid
        self.full_clean()  # Run validation
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class ManpowerExpense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='manpower_expenses')
    work_type = models.ForeignKey(LaborWorkType, on_delete=models.PROTECT, related_name='manpower_expenses', null=True, blank=True)
    date = models.DateField(default=timezone.now)
    number_of_people = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    per_person_cost = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.total_amount > self.project.budget:
            raise ValidationError({'total_amount': 'Total amount cannot exceed project budget'})

    def save(self, *args, **kwargs):
        self.total_amount = self.number_of_people * self.per_person_cost
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Manpower Expense - {self.project.name} - {self.date}"

    class Meta:
        ordering = ['-date']

class MaterialItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['display_name']

def create_default_material_items():
    default_items = [
        ('brick', 'Brick'),
        ('cement', 'Cement'),
        ('steel', 'Steel'),
        ('sand', 'Sand'),
        ('aggregate', 'Jelly'),
        ('paint', 'Paint'),
        ('tiles', 'Tiles'),
        ('wood', 'Wood'),
        ('stone pebbles', 'Stone pebbles'),
        ('grinate', 'Grinate'),
        ('electrical', 'Electrical Items'),
        ('plumbing', 'Plumbing Items'),
        ('others', 'Others')
    ]
    
    for code, name in default_items:
        MaterialItem.objects.get_or_create(
            name=code,
            defaults={'display_name': name}
        )

class MaterialExpense(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='material_expenses')
    date = models.DateField(default=timezone.now)
    item = models.ForeignKey(MaterialItem, on_delete=models.PROTECT, related_name='expenses')
    custom_item_name = models.CharField(max_length=100, null=True, blank=True)
    per_unit_cost = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    quantity = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.item.name == 'others' and not self.custom_item_name:
            raise ValidationError({'custom_item_name': 'Custom item name is required when "Others" is selected'})
        
        # Calculate total amount
        self.total_amount = self.per_unit_cost * self.quantity
        
        # Check if total amount exceeds project budget
        total_expenses = (
            ManpowerExpense.objects.filter(project=self.project).aggregate(total=Sum('total_amount'))['total'] or 0
        ) + (
            MaterialExpense.objects.filter(project=self.project).exclude(id=self.id).aggregate(total=Sum('total_amount'))['total'] or 0
        )
        
        if total_expenses + self.total_amount > self.project.budget:
            raise ValidationError({'total_amount': 'Total expenses would exceed project budget'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        item_name = self.custom_item_name if self.custom_item_name else self.item.display_name
        return f"Material Expense - {self.project.name} - {item_name} - {self.date}"

    class Meta:
        ordering = ['-date']

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('Advance', 'Advance Payment'),
        ('Installment', 'Installment Payment'),
        ('Full', 'Full Payment'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_date = models.DateField(default=timezone.now)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    description = models.TextField(blank=True, null=True)
    payment_file = models.FileField(upload_to='payment_files/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.payment_date > timezone.now().date():
            raise ValidationError({'payment_date': 'Payment date cannot be in the future'})
        if self.amount > self.project.budget:
            raise ValidationError({'amount': 'Payment amount cannot exceed project budget'})

    def save(self, *args, **kwargs):
        self.full_clean()
        # Update project's total_paid when a payment is saved
        if not self.pk:  # Only on creation
            self.project.total_paid += self.amount
            self.project.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Update project's total_paid when a payment is deleted
        self.project.total_paid -= self.amount
        self.project.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_type} - {self.amount} ({self.project.name})"

    class Meta:
        ordering = ['-payment_date']

