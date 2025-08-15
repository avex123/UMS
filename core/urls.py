from django.urls import path
from . import views
from .views import calendar_events, add_reminder, edit_reminder, delete_reminder

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('projects/<int:pk>/upload/', views.upload_project_file, name='upload_project_file'),
    path('projects/<int:pk>/add_cost/', views.add_production_cost, name='add_production_cost'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/new/', views.inventory_create, name='inventory_create'),
    path('inventory/add/', views.inventory_add_stock, name='inventory_add_stock'),
    path('tasks/', views.task_dashboard, name='task_dashboard'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('tasks/', views.task_dashboard, name='task_dashboard'),
    path('tasks/new/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    # Cutting List Routes
    path('cutting-lists/', views.cutting_list_dashboard, name='cutting_list_dashboard'),
    path('cutting-lists/new/', views.cutting_list_create, name='cutting_list_create'),
    path('cutting-lists/<int:pk>/', views.cutting_list_detail, name='cutting_list_detail'),
    path('cutting-lists/<int:pk>/pdf/', views.cutting_list_pdf_export, name='cutting_list_pdf'),
    path('quotes/', views.quote_dashboard, name='quote_dashboard'),
    path('quotes/new/', views.quote_create, name='quote_create'),
    path('quotes/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quotes/<int:pk>/pdf/', views.quote_pdf_export, name='quote_pdf'),
    path('calendar/events/', views.calendar_events, name='calendar_events'),
    # 🚚 Shipping URLs
    path('shipping/', views.shipping_dashboard, name='shipping_dashboard'),
    path('shipping/new/', views.shipment_create, name='shipment_create'),
    path('shipping/<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('shipping/new/', views.shipment_create, name='shipment_create'),
    path('messages/', views.conversation_list, name='conversation_list'),
    path('messages/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    path('chat/', views.chat_dashboard, name='chat_dashboard'),
    path('chat/create/', views.chat_create, name='chat_create'),  # 👈 add this
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),  # for viewing chat
    path('chat/new/', views.new_chat, name='new_chat'),
    path('invoices/', views.invoice_dashboard, name='invoice_dashboard'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('stats/', views.stats_dashboard, name='stats_dashboard'),
    path('calendar/events/', calendar_events, name='calendar_events'),
    path('calendar/add_reminder/', add_reminder, name='add_reminder'),
    path('calendar/edit_reminder/<int:reminder_id>/', edit_reminder, name='edit_reminder'),
    path('calendar/delete_reminder/<int:reminder_id>/', delete_reminder, name='delete_reminder'),
    path('users/', views.user_list, name='user_list'),
    path('users/assign-role/', views.assign_role, name='assign_role'),



    









    




    
]



