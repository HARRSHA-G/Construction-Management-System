from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, action
from django.db.models import Sum, Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from .models import Project, ManpowerExpense, MaterialExpense, Payment, LaborWorkType, MaterialItem
from .serializers import (
    ProjectSerializer, ManpowerExpenseSerializer, 
    MaterialExpenseSerializer, PaymentSerializer,
    LaborWorkTypeSerializer, MaterialItemSerializer
)
import logging
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal 



logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')

@ensure_csrf_cookie
def projects(request):
    return render(request, 'projects.html')

@ensure_csrf_cookie
def expenses(request):
    return render(request, 'expenses.html')

@ensure_csrf_cookie
def reports(request):
    return render(request, 'reports.html')

@ensure_csrf_cookie
def payments(request):
    return render(request, 'payments.html')

@method_decorator(csrf_protect, name='dispatch')
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            projects = self.get_queryset()
            serializer = self.get_serializer(projects, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in project list: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            logger.debug(f"Received POST data: {request.data}")
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in ProjectViewSet.create: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check if project_id is being updated
        if 'project_id' in request.data:
            new_project_id = request.data['project_id']
            # Check if the new project_id is already in use by another project
            if Project.objects.filter(project_id=new_project_id).exclude(id=instance.id).exists():
                return Response(
                    {'error': 'This Project ID is already in use'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # Check if project has any expenses or payments
            if (instance.manpower_expenses.exists() or 
                instance.material_expenses.exists() or 
                instance.payments.exists()):
                return Response(
                    {'error': 'Cannot delete project with existing expenses or payments'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

@api_view(['GET'])
def material_items_list(request):
    items = MaterialItem.objects.filter(is_active=True)
    serializer = MaterialItemSerializer(items, many=True)
    return Response(serializer.data)

@method_decorator(csrf_protect, name='dispatch')
class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'delete']
    
    def get_queryset(self):
        expense_type = self.request.query_params.get('type')
        project_id = self.request.query_params.get('project_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        search = self.request.query_params.get('search', '')

        # Base queryset based on expense type
        if expense_type == 'manpower':
            queryset = ManpowerExpense.objects.all()
        elif expense_type == 'material':
            queryset = MaterialExpense.objects.all()
        else:
            # Default to manpower expenses if no type specified
            queryset = ManpowerExpense.objects.all()

        # Filter by project if provided
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                queryset = queryset.filter(project=project)
            except Project.DoesNotExist:
                return ManpowerExpense.objects.none()

        # Apply date filters if provided
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                return ManpowerExpense.objects.none()

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                return ManpowerExpense.objects.none()

        # Apply search filter
        if search:
            if expense_type == 'manpower':
                queryset = queryset.filter(description__icontains=search)
            elif expense_type == 'material':
                queryset = queryset.filter(
                    Q(item__display_name__icontains=search) |
                    Q(custom_item_name__icontains=search) |
                    Q(description__icontains=search)
                )

        # Apply ordering
        queryset = queryset.order_by('-date', '-created_at')

        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            expense_type = self.request.data.get('type')
        else:
            expense_type = self.request.query_params.get('type')
            
        if expense_type == 'manpower':
            return ManpowerExpenseSerializer
        elif expense_type == 'material':
            return MaterialExpenseSerializer
        # Default to ManpowerExpenseSerializer if no type specified
        return ManpowerExpenseSerializer
    
    def create(self, request, *args, **kwargs):
        expense_type = request.data.get('type')
        project_id = request.data.get('project')
        
        if not project_id:
            return Response(
                {'error': 'Project ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not expense_type:
            return Response(
                {'error': 'Expense type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            if expense_type == 'manpower':
                return self._create_manpower_expense(request.data, project)
            elif expense_type == 'material':
                return self._create_material_expense(request.data, project)
            else:
                return Response(
                    {'error': 'Invalid expense type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error creating expense: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    def _create_manpower_expense(self, data, project):
        # Calculate available funds
        total_paid = Payment.objects.filter(project=project).aggregate(total=Sum('amount'))['total'] or 0
        total_expenses = (
            ManpowerExpense.objects.filter(project=project).aggregate(total=Sum('total_amount'))['total'] or 0
        ) + (
            MaterialExpense.objects.filter(project=project).aggregate(total=Sum('total_amount'))['total'] or 0
        )
        available_funds = max(total_paid - total_expenses, 0)
        try:
            amount = float(data.get('total_amount', 0))
        except Exception:
            amount = 0
        if available_funds <= 0:
            return Response(
                {'error': 'No funds available for expenses.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if amount > available_funds:
            return Response(
                {'error': 'Your funds are not sufficient to add this expense.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ManpowerExpenseSerializer(data=data)
        if serializer.is_valid():
            try:
                expense = serializer.save(project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _create_material_expense(self, data, project):
        try:
            # Get the material item
            item_id = data.get('item')
            if not item_id:
                return Response(
                    {'error': 'Material item is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                item = MaterialItem.objects.get(id=item_id)
            except MaterialItem.DoesNotExist:
                return Response(
                    {'error': 'Invalid material item'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate available funds
            total_paid = Payment.objects.filter(project=project).aggregate(total=Sum('amount'))['total'] or 0
            total_expenses = (
                ManpowerExpense.objects.filter(project=project).aggregate(total=Sum('total_amount'))['total'] or 0
            ) + (
                MaterialExpense.objects.filter(project=project).aggregate(total=Sum('total_amount'))['total'] or 0
            )
            available_funds = max(total_paid - total_expenses, 0)

            # Calculate total amount
            per_unit_cost = float(data.get('per_unit_cost', 0))
            quantity = float(data.get('quantity', 0))
            total_amount = per_unit_cost * quantity

            if available_funds <= 0:
                return Response(
                    {'error': 'No funds available for expenses.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if total_amount > available_funds:
                return Response(
                    {'error': 'Your funds are not sufficient to add this expense.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the expense
            expense_data = {
                'project': project.id,
                'date': data.get('date'),
                'item': item.id,
                'per_unit_cost': per_unit_cost,
                'quantity': quantity,
                'total_amount': total_amount,
                'description': data.get('description', '')
            }

            if item.name == 'others':
                custom_item_name = data.get('custom_item_name')
                if not custom_item_name:
                    return Response(
                        {'error': 'Custom item name is required when "Others" is selected'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                expense_data['custom_item_name'] = custom_item_name

            serializer = MaterialExpenseSerializer(data=expense_data)
            if serializer.is_valid():
                expense = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error creating material expense: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'Project ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get expense summaries
        manpower_expenses = ManpowerExpense.objects.filter(project=project)
        material_expenses = MaterialExpense.objects.filter(project=project)

        # Calculate totals
        manpower_total = manpower_expenses.aggregate(total=Sum('total_amount'))['total'] or 0
        material_total = material_expenses.aggregate(total=Sum('total_amount'))['total'] or 0

        # Get expense counts
        manpower_count = manpower_expenses.count()
        material_count = material_expenses.count()

        return Response({
            'manpower': {
                'total': manpower_total,
                'count': manpower_count
            },
            'material': {
                'total': material_total,
                'count': material_count
            },
            'total_expenses': manpower_total + material_total
        })

@csrf_protect
@api_view(['GET'])
def report_data(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        time_range = request.query_params.get('time_range', 'month')
        
        # Calculate date range based on time_range
        today = timezone.now().date()
        if time_range == 'month':
            start_date = today.replace(day=1)
        elif time_range == 'quarter':
            current_quarter = (today.month - 1) // 3
            start_date = today.replace(month=current_quarter * 3 + 1, day=1)
        else:  # year
            start_date = today.replace(month=1, day=1)
        
        # --- OVERALL STATS (not filtered by time) ---
        all_manpower_expenses = ManpowerExpense.objects.filter(project_id=project_id)
        all_material_expenses = MaterialExpense.objects.filter(project_id=project_id)
        all_payments = Payment.objects.filter(project_id=project_id)

        overall_total_manpower = all_manpower_expenses.aggregate(total=Sum('total_amount'))['total'] or 0
        overall_total_material = all_material_expenses.aggregate(total=Sum('total_amount'))['total'] or 0
        overall_total_expenses = overall_total_manpower + overall_total_material
        overall_total_payments = all_payments.aggregate(total=Sum('amount'))['total'] or 0
        overall_due_payments = project.budget - overall_total_payments
        overall_available_funds = max(overall_total_payments - overall_total_expenses, 0)
        overall_budget_utilization = (overall_total_expenses / project.budget * 100) if project.budget > 0 else 0

        # --- FILTERED DATA (for charts) ---
        manpower_expenses = all_manpower_expenses.filter(date__gte=start_date, date__lte=today)
        material_expenses = all_material_expenses.filter(date__gte=start_date, date__lte=today)
        payments = all_payments.filter(payment_date__gte=start_date, payment_date__lte=today)
        
        total_manpower = manpower_expenses.aggregate(total=Sum('total_amount'))['total'] or 0
        total_material = material_expenses.aggregate(total=Sum('total_amount'))['total'] or 0
        total_expenses = total_manpower + total_material
        
        expense_breakdown = {
            'Manpower': total_manpower,
            'Material': total_material
        }

        payment_breakdown = {}
        for payment_type in ['Advance', 'Installment', 'Full']:
            type_payments = payments.filter(payment_type=payment_type)
            total = type_payments.aggregate(total=Sum('amount'))['total'] or 0
            payment_breakdown[payment_type] = total

        total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
        due_payments = project.budget - total_payments
        available_funds = max(total_payments - total_expenses, 0)
        budget_utilization = (total_expenses / project.budget * 100) if project.budget > 0 else 0

        # Get monthly expense trend
        monthly_expenses = []
        monthly_payments = []
        current_date = start_date
        while current_date <= today:
            month_end = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            
            month_expenses = manpower_expenses.filter(
                date__year=current_date.year,
                date__month=current_date.month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            month_expenses += material_expenses.filter(
                date__year=current_date.year,
                date__month=current_date.month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            month_payments = payments.filter(
                payment_date__year=current_date.year,
                payment_date__month=current_date.month
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_expenses.append({
                'date': current_date.strftime('%Y-%m'),
                'amount': month_expenses
            })
            
            monthly_payments.append({
                'date': current_date.strftime('%Y-%m'),
                'amount': month_payments
            })
            
            current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)

        return Response({
            'project_name': project.name,
            'budget': project.budget,
            # --- OVERALL STATS ---
            'overall': {
                'total_expenses': overall_total_expenses,
                'total_payments': overall_total_payments,
                'available_funds': overall_available_funds,
                'due_payments': overall_due_payments,
                'budget_utilization': round(overall_budget_utilization, 2),
            },
            # --- FILTERED DATA (for charts) ---
            'filtered': {
                'total_expenses': total_expenses,
                'total_payments': total_payments,
                'available_funds': available_funds,
                'due_payments': due_payments,
                'budget_utilization': round(budget_utilization, 2),
                'expense_breakdown': expense_breakdown,
                'payment_breakdown': payment_breakdown,
                'monthly_trend': {
                    'expenses': monthly_expenses,
                    'payments': monthly_payments
                }
            }
        })
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in report_data: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_protect, name='dispatch')
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            logger.debug(f"Received POST data for payment: {request.data}")
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in PaymentViewSet.create: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            payments = self.get_queryset()
            serializer = self.get_serializer(payments, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in payment list: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        if project_id:
            return Payment.objects.filter(project_id=project_id)
        return Payment.objects.all()

@csrf_protect
@api_view(['GET'])
def project_payments(request, project_id):
    try:
        payments = Payment.objects.filter(project_id=project_id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error in project_payments: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def labor_work_type_list(request):
    work_types = LaborWorkType.objects.all()
    serializer = LaborWorkTypeSerializer(work_types, many=True)
    return Response(serializer.data)
