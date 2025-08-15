from django.db import models
from django.contrib.auth.models import User
import uuid



class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    DIVISION_CHOICES = [
        ('UMS', 'UMS – CNC Services'),
        ('UZUN', 'Uzun-Pak – Food Packaging'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    division = models.CharField(max_length=10, choices=DIVISION_CHOICES, default='UMS')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")

    # 💰 Pricing Fields
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    production_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def profit_margin(self):
        if self.selling_price and self.production_cost:
            return self.selling_price - self.production_cost
        return None

    def __str__(self):
        return f"{self.name} ({self.get_division_display()})"


class MaterialType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Material Type"
        verbose_name_plural = "Material Types"

    def __str__(self):
        return self.name


class StockType(models.Model):
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, related_name="stock_types")
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Stock Type"
        verbose_name_plural = "Stock Types"
        unique_together = ('material_type', 'name')

    def __str__(self):
        return f"{self.material_type.name} - {self.name}"


class InventoryItem(models.Model):
    stock_type = models.ForeignKey(
        'StockType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items'
    )
    name = models.CharField(max_length=255, blank=True, null=True, default="Unknown")
    dimensions = models.CharField(max_length=255, default="N/A")
    length = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Length per piece (in meters)")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default="m", help_text="e.g., m for meters")
    serial_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    @property
    def total_length(self):
        if self.length and self.quantity:
            return float(self.length) * float(self.quantity)
        return 0.0  # Return 0 if either is missing


    def save(self, *args, **kwargs):
        if not self.serial_number and self.stock_type:
            material_initials = self.stock_type.material_type.name[:2].upper()
            stock_initials = self.stock_type.name[:2].upper()
            prefix = f"{material_initials}-{stock_initials}"
            existing = InventoryItem.objects.filter(serial_number__startswith=prefix).count()
            next_number = existing + 1
            self.serial_number = f"{prefix}{str(next_number).zfill(3)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stock_type} | {self.name} | {self.dimensions} | {self.serial_number}"


class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Detailed instructions for this task")  # 🆕
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')  # 🆕 ForeignKey
    due_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    progress = models.PositiveIntegerField(default=0, help_text="Progress percentage (0-100)")  # 🆕
    task_file = models.FileField(upload_to='task_files/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.status}"


class ProjectFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('3D', '3D Model'),
        ('DRAWING', 'Technical Drawing'),
        ('INVOICE', 'Invoice'),
        ('OTHER', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='project_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='OTHER')

    def __str__(self):
        return f"{self.file.name} ({self.get_file_type_display()})"


class ProductionCost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="production_costs")
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_file = models.ForeignKey(ProjectFile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} ({self.amount} BAM)"
    


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.name}"

class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    file = models.FileField(upload_to='project_comments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.name}"
    
    
class CuttingList(models.Model):
    name = models.CharField(max_length=255, help_text="Name for this cutting list (e.g., Project ABC - Pipes)")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CuttingListEntry(models.Model):
    cutting_list = models.ForeignKey(CuttingList, on_delete=models.CASCADE, related_name='entries')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    cut_length = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cut length (mm)")
    quantity = models.PositiveIntegerField()
    total_length_used = models.DecimalField(max_digits=10, decimal_places=2, help_text="Auto-calculated: cut_length * quantity", default=0)
    waste = models.DecimalField(max_digits=10, decimal_places=2, help_text="Remaining offcut after cuts", default=0)

    def __str__(self):
        return f"{self.quantity}x {self.cut_length}mm from {self.inventory_item.name}"


class Quote(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='quotes')
    project_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[
        ('Draft', 'Draft'),
        ('Sent', 'Sent to Customer'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ], default='Draft')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Quote #{self.id} - {self.project_name} ({self.customer.name})"

    @property
    def total_cost(self):
        return sum(item.total_price for item in self.items.all())


class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} ({self.quantity} x {self.unit_price})"

class Shipment(models.Model):
    SHIPMENT_TYPES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    shipment_type = models.CharField(max_length=20, choices=SHIPMENT_TYPES)
    name = models.CharField(max_length=200)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    expected_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, default="Pending")
    notes = models.TextField(blank=True, null=True)


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(Shipment, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.description} ({self.quantity})"

class Conversation(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)  # For group chats
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Conversation {self.id}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} at {self.timestamp}"
    
class ChatRoom(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)  # blank for private chats
    participants = models.ManyToManyField(User, related_name="chat_rooms")
    is_group = models.BooleanField(default=False)

    def __str__(self):
        return self.name or f"Chat {self.id}"


class Chat(models.Model):
    CHAT_TYPE_CHOICES = [
        ('private', 'Private'),
        ('group', 'Group'),
    ]

    name = models.CharField(max_length=255)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES, default='private')
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_chat_type_display()})"


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_uploads/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.chat.name}"
    
    
class Invoice(models.Model):
    PROJECT_CATEGORIES = [
        ('PARTS', 'Parts'),
        ('MATERIALS', 'Materials'),
        ('SERVICES', 'Services'),
        ('OTHER', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices')
    category = models.CharField(max_length=20, choices=PROJECT_CATEGORIES)
    date_received = models.DateField(auto_now_add=True)
    uploaded_file = models.FileField(upload_to='invoices/')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Invoice {self.id} - {self.project.name} ({self.get_category_display()})"

class InvoiceMaterial(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='materials')
    material = models.ForeignKey(InventoryItem, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} ({self.quantity})"    
    
class ProjectCost(models.Model):
    PROJECT_COST_TYPES = [
        ('materials', 'Materials'),
        ('services', 'Services'),
        ('revisions', 'Revisions'),
        ('other', 'Other'),
    ]
    project = models.ForeignKey(Project, related_name="costs", on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=PROJECT_COST_TYPES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    
# models.py
class Reminder(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} on {self.date}"
    
    
class UserRole(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("production", "Production"),
        ("qc", "Quality Control"),
        ("sales", "Sales"),
        ("finance", "Finance"),
        ("procurement", "Procurement"),
        ("Director", "Director"),
        ("CNC Operator", "CNC Operator"),
        ("Production Manager", "Production Manager"),
        ("CAD Designer", "CAD Designer"),
        ("Owner", "Owner"),
        ("Manual Labour", "Manual Labour"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userrole")
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, blank=True)

    def __str__(self):
        display = dict(self.ROLE_CHOICES).get(self.role, "No role")
        return f"{self.user.username} — {display}"    