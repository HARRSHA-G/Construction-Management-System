from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project, Expense
from .serializers import ProjectSerializer, ExpenseSerializer
from django.db.models import Sum
from collections import defaultdict

def index(request):
    return render(request, 'index.html')

def projects(request):
    return render(request, 'projects.html')

def expenses(request):
    return render(request, 'expenses.html')

def analytics(request):
    return render(request, 'analytics.html')

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

@api_view(['GET'])
def analytics_data(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        expenses = Expense.objects.filter(project=project)
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        expense_breakdown = defaultdict(float)
        for expense in expenses:
            expense_breakdown[expense.category] += float(expense.amount)
        data = {
            'project_name': project.name,
            'budget': float(project.budget),
            'total_expenses': float(total_expenses),
            'expense_breakdown': dict(expense_breakdown)
        }
        return Response(data)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=404)