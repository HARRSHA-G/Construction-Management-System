from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, ExpenseViewSet,
    PaymentViewSet,
    labor_work_type_list,
    report_data,
    material_items_list
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/labor-work-types/', labor_work_type_list, name='labor-work-type-list'),
    path('api/reports/<int:project_id>/', report_data, name='report-data'),
    path('labor-work-types/', labor_work_type_list, name='labor-work-types-list'),
    path('material-items/', material_items_list, name='material-items-list'),
] 