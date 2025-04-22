from rest_framework import serializers
from .models import Project, Expense

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'land_details', 'land_address', 'budget', 'status', 'document', 'created_at', 'updated_at']

class ExpenseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'project', 'project_name', 'category', 'amount', 'date', 'description', 'created_at', 'updated_at']