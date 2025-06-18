from rest_framework import serializers
from .models import Project, ManpowerExpense, MaterialExpense, Payment, LaborWorkType, MaterialItem
import logging
from django.db.models import Sum

logger = logging.getLogger(__name__)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'project_id', 'name', 'land_details', 'land_address', 'budget', 'duration_months', 'status', 'total_paid', 'remaining_amount']
        read_only_fields = []  # Remove any read-only fields

    def validate_project_id(self, value):
        if not value.startswith('ID-'):
            raise serializers.ValidationError("Project ID must start with 'ID-'")
        
        # Check if the rest of the ID is alphanumeric
        id_part = value[3:]  # Get the part after 'ID-'
        if not id_part.isalnum():
            raise serializers.ValidationError("Project ID must contain only letters and numbers after 'ID-'")
        
        # Check if this project_id already exists for a different project
        if self.instance and self.instance.project_id != value:
            if Project.objects.filter(project_id=value).exists():
                raise serializers.ValidationError("This Project ID is already in use")
        elif not self.instance and Project.objects.filter(project_id=value).exists():
            raise serializers.ValidationError("This Project ID is already in use")
                
        return value

    def validate_budget(self, value):
        if value <= 0:
            logger.warning(f"Invalid budget: {value}")
            raise serializers.ValidationError("Budget must be greater than zero.")
        return value

    def validate_duration_months(self, value):
        if value < 1:
            logger.warning(f"Invalid duration: {value}")
            raise serializers.ValidationError("Duration must be at least 1 month.")
        return value

    def validate_document(self, value):
        if value:
            if not value.name.endswith('.pdf'):
                logger.warning(f"Invalid file type for document: {value.name}")
                raise serializers.ValidationError("Document must be a PDF file.")
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                logger.warning(f"File too large: {value.size} bytes")
                raise serializers.ValidationError("Document must be smaller than 5MB.")
        return value

class PaymentSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'project', 'project_name', 'amount', 'payment_date', 'payment_type', 'payment_file']
        read_only_fields = ['project_name']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

    def validate_payment_file(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                raise serializers.ValidationError("File size must be less than 5MB")
        return value

class LaborWorkTypeSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = LaborWorkType
        fields = ['id', 'name', 'name_display', 'description']

class ManpowerExpenseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    work_type_display = serializers.CharField(source='work_type.get_name_display', read_only=True)

    class Meta:
        model = ManpowerExpense
        fields = ['id', 'project', 'project_name', 'work_type', 'work_type_display', 'date', 'number_of_people', 'per_person_cost', 'total_amount', 'description']
        read_only_fields = ['total_amount', 'work_type_display']

    def validate(self, data):
        if data.get('number_of_people', 0) <= 0:
            raise serializers.ValidationError({'number_of_people': 'Number of people must be greater than 0'})
        if data.get('per_person_cost', 0) <= 0:
            raise serializers.ValidationError({'per_person_cost': 'Per person cost must be greater than 0'})
        return data

    def create(self, validated_data):
        number_of_people = validated_data.get('number_of_people')
        per_person_cost = validated_data.get('per_person_cost')
        validated_data['total_amount'] = number_of_people * per_person_cost
        return super().create(validated_data)

class MaterialItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialItem
        fields = ['id', 'name', 'display_name', 'is_active']

class MaterialExpenseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    item_display = serializers.CharField(source='item.display_name', read_only=True)

    class Meta:
        model = MaterialExpense
        fields = ['id', 'project', 'project_name', 'date', 'item', 'item_display', 'custom_item_name', 
                 'per_unit_cost', 'quantity', 'total_amount', 'description', 'created_at', 'updated_at']
        read_only_fields = ['total_amount', 'created_at', 'updated_at', 'item_display']

    def validate(self, data):
        if data.get('item').name == 'others' and not data.get('custom_item_name'):
            raise serializers.ValidationError({
                'custom_item_name': 'Custom item name is required when "Others" is selected'
            })
        if data.get('per_unit_cost', 0) <= 0:
            raise serializers.ValidationError({'per_unit_cost': 'Per unit cost must be greater than 0'})
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError({'quantity': 'Quantity must be greater than 0'})
        
        # Calculate total amount
        per_unit_cost = data.get('per_unit_cost')
        quantity = data.get('quantity')
        if per_unit_cost and quantity:
            data['total_amount'] = per_unit_cost * quantity
            
            # Check if total amount exceeds project budget
            project = data.get('project')
            if project:
                total_expenses = (
                    ManpowerExpense.objects.filter(project=project).aggregate(total=Sum('total_amount'))['total'] or 0
                ) + (
                    MaterialExpense.objects.filter(project=project).exclude(id=self.instance.id if self.instance else None).aggregate(total=Sum('total_amount'))['total'] or 0
                )
                
                if total_expenses + data['total_amount'] > project.budget:
                    raise serializers.ValidationError({
                        'total_amount': 'Total expenses would exceed project budget'
                    })
        
        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
