from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('item/add-edit/', views.add_or_edit_item, name='add_or_edit'),
    path('item/delete/<int:pk>/', views.delete_item, name='delete_item'),
    path('item/update/<int:pk>/<str:action>/', views.update_stock, name='update_stock'),
    path('history/clear/', views.clear_history, name='clear_history'),
    path('export/', views.export_csv, name='export_csv'),
    path('import/', views.import_csv, name='import_csv'),
]