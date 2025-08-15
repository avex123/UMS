from django import forms
from .models import Project, ProjectFile
from .models import Project, ProjectFile, ProductionCost  # ← make sure ProductionCost is here
from .models import Customer
from django import forms
from .models import Customer
from .models import InventoryItem, MaterialType, StockType
from django.utils import timezone
from .models import Task
from .models import ProjectComment
from .models import CuttingList, CuttingListEntry
from django.forms import inlineformset_factory
from django.forms import modelformset_factory
from .models import CuttingListEntry
from django.forms import inlineformset_factory
from .models import Quote, QuoteItem
from django.forms import inlineformset_factory
from .models import Quote, QuoteItem
from django import forms
from .models import Shipment, ShipmentItem
from .models import Message





class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'division', 'selling_price', 'production_cost']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'division': forms.Select(attrs={'class': 'form-select'}),
            'selling_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'production_cost': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['file', 'description', 'file_type']
        widgets = {
            'file_type': forms.Select(attrs={'class': 'form-select'})
        }

class ProductionCostForm(forms.ModelForm):
    class Meta:
        model = ProductionCost
        fields = ['description', 'amount', 'invoice_file']
        widgets = {
            'invoice_file': forms.Select(attrs={'class': 'form-select'})
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'company_name', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3}),
        }        
   
   
from django import forms
from .models import InventoryItem, MaterialType, StockType

class InventoryItemForm(forms.ModelForm):
    material = forms.ModelChoiceField(
        queryset=MaterialType.objects.all(),
        label="Material",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg shadow-sm mb-3',
            'style': 'border-radius: 10px; border: 1px solid #dc3545;',
        })
    )

    class Meta:
        model = InventoryItem
        fields = ['material', 'stock_type', 'name', 'length', 'quantity']
        widgets = {
            'stock_type': forms.Select(attrs={
                'class': 'form-select form-select-lg shadow-sm mb-3',
                'style': 'border-radius: 10px; border: 1px solid #dc3545;',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control shadow-sm mb-3',
                'placeholder': 'e.g., 50x50x2 Square Tube',
                'style': 'border-radius: 10px;',
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control shadow-sm mb-3',
                'placeholder': 'Length (mm)',
                'style': 'border-radius: 10px;',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control shadow-sm mb-3',
                'placeholder': 'Quantity',
                'style': 'border-radius: 10px;',
            }),
        }

    def __init__(self, *args, **kwargs):
        # Call parent's constructor first to avoid missing fields
        super(InventoryItemForm, self).__init__(*args, **kwargs)

        # Set stock_type queryset to none initially
        self.fields['stock_type'].queryset = StockType.objects.none()

        # Populate stock_type if material is provided in POST or instance
        if 'material' in self.data:
            try:
                material_id = int(self.data.get('material'))
                self.fields['stock_type'].queryset = StockType.objects.filter(material_type_id=material_id)
            except (ValueError, TypeError):
                pass  # invalid input; ignore and leave empty
        elif self.instance.pk and self.instance.stock_type:
            self.fields['stock_type'].queryset = StockType.objects.filter(
                material_type=self.instance.stock_type.material_type
            )

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'name', 'description', 'assigned_to', 'due_date', 'status', 'progress', 'task_file']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }
      
from .models import TaskComment

class TaskCommentForm(forms.ModelForm):
    class Meta:
        model = TaskComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your update here...'}),
        }
        
class ProjectCommentForm(forms.ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['comment', 'file']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your comment here...',
                'class': 'form-control'
            }),
        }
        
class CuttingListForm(forms.ModelForm):
    class Meta:
        model = CuttingList
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for this cutting list'}),
        }

class CuttingListEntryForm(forms.ModelForm):
    class Meta:
        model = CuttingListEntry
        fields = ['inventory_item', 'cut_length', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit materials to those with quantity > 0 (optional)
        self.fields['inventory_item'].queryset = InventoryItem.objects.filter(quantity__gt=0)

        # Customize material dropdown display
        self.fields['inventory_item'].label_from_instance = lambda obj: (
            f"{obj.serial_number} | {obj.dimensions} | {obj.length:.2f}m"
        )

CuttingListEntryFormSet = modelformset_factory(
    CuttingListEntry,
    form=CuttingListEntryForm,  # 👈 Use the custom form for each row
    extra=1,
    can_delete=True
)

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['customer', 'project_name', 'description', 'status', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class QuoteItemForm(forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

QuoteItemFormSet = inlineformset_factory(
    Quote, QuoteItem, form=QuoteItemForm, extra=1, can_delete=True
)

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = '__all__'


class ShipmentItemForm(forms.ModelForm):
    class Meta:
        model = ShipmentItem
        fields = ['description', 'quantity', 'unit']

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['shipment_type', 'name', 'tracking_number', 'expected_date', 'status', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if isinstance(self.fields[field].widget, forms.Select):
                self.fields[field].widget.attrs.update({'class': 'form-select'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message...'}),
        }
        
from django import forms
from .models import Chat, ChatMessage


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['name', 'chat_type', 'participants']
        widgets = {
            'participants': forms.CheckboxSelectMultiple(),
        }


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'file']
        
        
        
from .models import Invoice, InvoiceMaterial
from django.forms import modelformset_factory

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['project', 'category', 'uploaded_file']

class InvoiceMaterialForm(forms.ModelForm):
    class Meta:
        model = InvoiceMaterial
        fields = ['description', 'quantity', 'unit_price', 'material']

InvoiceMaterialFormSet = modelformset_factory(
    InvoiceMaterial,
    form=InvoiceMaterialForm,
    extra=1,
    can_delete=True
)
        