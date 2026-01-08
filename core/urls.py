from django.urls import path
from auth_sys import views

urlpatterns = [
    # Auth
    path('api/register/', views.register),
    path('api/login/', views.login),
    path('api/logout/', views.logout),
    path('api/profile/', views.update_profile),
    path('api/delete/', views.delete_account),
    
    # Admin / Permissions
    path('api/permissions/', views.manage_permissions),
    
    # Mock Business Logic
    path('api/reports/', views.get_reports),
    path('api/reports/create/', views.create_report),
]