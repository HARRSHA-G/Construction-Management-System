from django.contrib import admin
from .models import Project, ManpowerExpense, MaterialExpense, Payment, LaborWorkType, MaterialItem

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'name', 'budget', 'status', 'total_paid', 'remaining_amount')
    search_fields = ('project_id', 'name', 'land_details', 'land_address')
    list_filter = ('status',)

@admin.register(ManpowerExpense)
class ManpowerExpenseAdmin(admin.ModelAdmin):
    list_display = ('project', 'date', 'number_of_people', 'per_person_cost', 'total_amount')
    list_filter = ('date', 'project')
    search_fields = ('project__name', 'description')

@admin.register(MaterialExpense)
class MaterialExpenseAdmin(admin.ModelAdmin):
    list_display = ('project', 'date', 'item', 'quantity', 'per_unit_cost', 'total_amount')
    list_filter = ('date', 'project', 'item')
    search_fields = ('project__name', 'item', 'custom_item_name', 'description')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('project', 'amount', 'payment_date', 'payment_type')
    list_filter = ('payment_date', 'payment_type', 'project')
    search_fields = ('project__name', 'description')

@admin.register(LaborWorkType)
class LaborWorkTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(MaterialItem)
class MaterialItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active', 'created_at')
    search_fields = ('name', 'display_name')
    list_filter = ('is_active',)
    ordering = ('display_name',)