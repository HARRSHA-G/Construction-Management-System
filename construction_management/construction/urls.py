from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from construction.views import ProjectViewSet, ExpenseViewSet, index, projects, expenses, analytics
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', index, name='index'),
    path('projects/', projects, name='projects'),
    path('expenses/', expenses, name='expenses'),
    path('analytics/', analytics, name='analytics'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)