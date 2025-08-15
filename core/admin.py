from django.contrib import admin
from .models import (
    Project, 
    Task, 
    Customer, 
    MaterialType, 
    StockType, 
    InventoryItem, 
    ProjectFile, 
    ProductionCost
)
from django.contrib import admin
from .models import Shipment, ShipmentItem

# Inline display of projects under a customer
class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    readonly_fields = ('name', 'start_date', 'end_date', 'division')
    can_delete = False

# Customer admin configuration
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')
    inlines = [ProjectInline]

# Project admin
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'start_date', 'end_date')
    list_filter = ('division',)
    search_fields = ('name', 'description')

# Task admin
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'due_date')
    list_filter = ('status', 'project__division')
    search_fields = ('name', 'assigned_to')

# MaterialType admin
@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']

# StockType admin
@admin.register(StockType)
class StockTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'material_type']
    list_filter = ['material_type']
    search_fields = ['name']

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'stock_type', 'name', 'dimensions', 'length', 'quantity', 'total_length_display', 'unit']
    list_filter = ['stock_type__material_type', 'stock_type']
    search_fields = ['serial_number', 'name', 'dimensions']
    readonly_fields = ['serial_number', 'total_length_display']
    fieldsets = (
        (None, {
            'fields': ('stock_type', 'name', 'dimensions', 'length', 'quantity', 'unit', 'serial_number', 'total_length_display')
        }),
    )

    def total_length_display(self, obj):
        return f"{obj.total_length:.2f} m"
    total_length_display.short_description = "Total Length"


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipment_type', 'name', 'tracking_number', 'expected_date', 'status')
    list_filter = ('shipment_type', 'status', 'expected_date')
    search_fields = ('name', 'tracking_number', 'notes')

@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'description', 'quantity', 'unit')
    search_fields = ('description',)
