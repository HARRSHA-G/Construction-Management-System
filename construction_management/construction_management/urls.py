from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from construction import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('projects/', views.projects, name='projects'),
    path('expenses/', views.expenses, name='expenses'),
    path('reports/', views.reports, name='reports'),
    path('payments/', views.payments, name='payments'),
    path('api/', include(router.urls)),
    path('api/reports/<int:project_id>/', views.report_data, name='report_data'),
    path('api/labor-work-types/', views.labor_work_type_list, name='labor-work-type-list'),
    path('api/', include('construction.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
