from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectFile, ProductionCost
from .forms import ProjectForm, ProjectFileForm, ProductionCostForm
from .models import Customer
from .forms import CustomerForm  # We'll create this form next
from .models import MaterialType, StockType, InventoryItem
from .forms import InventoryItemForm  # we’ll create this
from .models import InventoryItem, MaterialType, StockType
from .models import Task
from .forms import TaskForm
from .forms import TaskCommentForm
from .models import CuttingList, CuttingListEntry
from .forms import CuttingListForm
from django.http import HttpResponse
from django.template.loader import render_to_string
# We'll use this later for PDF export
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from weasyprint import HTML
from django.template.loader import render_to_string
import tempfile
from .forms import CuttingListForm, CuttingListEntryForm
from .forms import CuttingListForm, CuttingListEntryFormSet
from decimal import Decimal
from weasyprint import HTML
from django.template.loader import get_template
from .models import Quote, QuoteItem
from .forms import QuoteForm, QuoteItemFormSet
from django.template.loader import get_template
from weasyprint import HTML

from django.shortcuts import render
from django.utils import timezone

from .models import Project, Task, InventoryItem, Quote, CuttingList
from django.http import JsonResponse
from .models import Task, Project, Quote

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Shipment, ShipmentItem
from .forms import ShipmentForm, ShipmentItemForm
from django import forms
from .models import Shipment
from django.db import models




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from .forms import MessageForm


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Chat, ChatMessage
from .forms import ChatForm, ChatMessageForm

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from django.contrib.auth.models import User  # already present in your file
# Q is already imported later in your file; we can use it here.

from django.db.models import Q  # if you prefer, keep this line; harmless if Q also imported later




def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after login
        else:
            return render(request, 'core/login.html', {'error': 'Invalid username or password'})
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login screen after logout


def dashboard(request):
    total_projects = Project.objects.count()
    active_tasks = Task.objects.filter(status="In Progress").count()
    total_inventory_items = InventoryItem.objects.count()
    pending_quotes = Quote.objects.filter(status="Pending").count()

    # 🆕 New KPIs
    today = timezone.now().date()
    overdue_tasks = Task.objects.filter(status__in=["Pending", "In Progress"], due_date__lt=today).count()
    low_stock_items = InventoryItem.objects.filter(length__lt=1.0).count()  # adjust threshold as needed
    projects_in_progress = Project.objects.filter(
        start_date__lte=today
    ).filter(
        end_date__isnull=True
    ) | Project.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    )
    projects_in_progress = projects_in_progress.count()

    return render(request, "core/dashboard.html", {
        "total_projects": total_projects,
        "active_tasks": active_tasks,
        "total_inventory_items": total_inventory_items,
        "pending_quotes": pending_quotes,
        "overdue_tasks": overdue_tasks,
        "low_stock_items": low_stock_items,
        "projects_in_progress": projects_in_progress,
    })

@login_required
def project_list(request):
    all_projects = Project.objects.all()

    print("\n=== DEBUG: ALL PROJECTS ===")
    for p in all_projects:
        print(f"{p.name} | division: '{p.division}'")

    ums_projects = all_projects.filter(division__icontains='UMS')
    uzun_projects = all_projects.filter(division__icontains='UZUN')

    return render(request, 'core/project_list.html', {
        'ums_projects': ums_projects,
        'uzun_projects': uzun_projects
    })


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            cleaned_division = form.cleaned_data['division']
            print("Division from form.cleaned_data:", cleaned_division)

            project = form.save(commit=False)
            project.division = cleaned_division
            project.save()
            return redirect('project_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    return redirect('project_list')


@login_required
def upload_project_file(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            project_file = form.save(commit=False)
            project_file.project = project
            project_file.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectFileForm()
    return render(request, 'core/upload_file.html', {'form': form, 'project': project})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Get all uploaded files
    files = project.files.all().order_by('-uploaded_at')

    # Group files into sections
    file_type_labels = [
        ('3D', '3D Models'),
        ('DRAWING', 'Technical Drawings'),
        ('INVOICE', 'Invoices'),
        ('OTHER', 'Other'),
    ]
    file_sections = []
    for code, label in file_type_labels:
        grouped_files = files.filter(file_type=code)
        file_sections.append({
            'code': code,
            'label': label,
            'files': grouped_files
        })

    # Get all production costs
    cost_entries = ProductionCost.objects.filter(project=project).select_related('invoice_file')
    total_cost = sum(entry.amount for entry in cost_entries)

    form = ProjectFileForm()
    cost_form = ProductionCostForm()

    return render(request, 'core/project_detail.html', {
        'project': project,
        'form': form,
        'cost_form': cost_form,
        'cost_entries': cost_entries,
        'total_cost': total_cost,
        'file_sections': file_sections,
    })


@login_required
def add_production_cost(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        invoice_file_id = request.POST.get('invoice_file_id')
        invoice_file = ProjectFile.objects.get(pk=invoice_file_id) if invoice_file_id else None

        ProductionCost.objects.create(
            project=project,
            description=description,
            amount=amount,
            invoice_file=invoice_file
        )
    return redirect('project_detail', pk=pk)

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    return render(request, 'core/customer_list.html', {'customers': customers})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'core/customer_detail.html', {'customer': customer})

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'core/customer_form.html', {'form': form})
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'core/add_customer.html', {'form': form})

@login_required
def inventory_list(request):
    materials = MaterialType.objects.all()
    selected_material_id = request.GET.get('material')
    selected_stock_id = request.GET.get('stock')

    stock_types = StockType.objects.filter(material_type_id=selected_material_id) if selected_material_id else []
    inventory_items = InventoryItem.objects.filter(stock_type_id=selected_stock_id) if selected_stock_id else []

    context = {
        'materials': materials,
        'stock_types': stock_types,
        'inventory_items': inventory_items,
        'selected_material_id': int(selected_material_id) if selected_material_id else None,
        'selected_stock_id': int(selected_stock_id) if selected_stock_id else None,
    }
    return render(request, 'core/inventory_list.html', context)



@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        # Pre-fill material from GET for filtering stock types
        initial_material = request.GET.get('material')
        form = InventoryItemForm(initial={'material': initial_material} if initial_material else None)

    return render(request, 'core/inventory_form.html', {'form': form})




@login_required
def inventory_add_stock(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = InventoryItemForm()

    return render(request, 'core/inventory_form.html', {'form': form})

@login_required
def task_dashboard(request):
    # Get all tasks ordered by due date
    tasks = Task.objects.select_related('project', 'assigned_to').order_by('due_date')

    ums_tasks = tasks.filter(project__division='UMS')
    uzun_tasks = tasks.filter(project__division='UZUN')

    return render(request, 'core/task_dashboard.html', {
        'ums_tasks': ums_tasks,
        'uzun_tasks': uzun_tasks
    })

@login_required
def my_tasks(request):
    user_tasks = Task.objects.filter(assigned_to=request.user).select_related('project')
    return render(request, 'core/my_tasks.html', {'tasks': user_tasks})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('task_dashboard')
    else:
        form = TaskForm()
    return render(request, 'core/task_form.html', {'form': form})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.select_related('user').order_by('-created_at')

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            comment_form = TaskCommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.task = task
                new_comment.user = request.user
                new_comment.save()
                return redirect('task_detail', pk=pk)

        if 'update_status' in request.POST:
            new_status = request.POST.get('status')
            new_progress = request.POST.get('progress')
            task.status = new_status
            task.progress = new_progress
            task.save()
            return redirect('task_detail', pk=pk)
    else:
        comment_form = TaskCommentForm()

    return render(request, 'core/task_detail.html', {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
    })
    
@login_required
def cutting_list_dashboard(request):
    cutting_lists = CuttingList.objects.all().order_by('-created_at')

    # Pre-calculate totals for each cutting list
    for cl in cutting_lists:
        total_used = sum(entry.total_length_used for entry in cl.entries.all())
        total_waste = sum(entry.waste for entry in cl.entries.all())
        cl.total_used = total_used
        cl.total_waste = total_waste

    return render(request, 'core/cutting_list_dashboard.html', {
        'cutting_lists': cutting_lists
    })



from decimal import Decimal

@login_required
def cutting_list_create(request):
    if request.method == 'POST':
        form = CuttingListForm(request.POST)
        formset = CuttingListEntryFormSet(request.POST, queryset=CuttingListEntry.objects.none())

        if form.is_valid() and formset.is_valid():
            cutting_list = form.save(commit=False)
            cutting_list.created_by = request.user
            cutting_list.save()

            for entry_form in formset:
                if entry_form.cleaned_data and not entry_form.cleaned_data.get('DELETE', False):
                    cutting_entry = entry_form.save(commit=False)
                    cutting_entry.cutting_list = cutting_list

                    # Total cut length (in meters) as Decimal
                    total_cut_length_m = (cutting_entry.cut_length * cutting_entry.quantity) / Decimal('1000')

                    # Update inventory length
                    inventory_item = cutting_entry.inventory_item
                    if inventory_item.length >= total_cut_length_m:
                        inventory_item.length -= total_cut_length_m
                        cutting_entry.waste = Decimal('0')  # No waste
                    else:
                        cutting_entry.waste = (total_cut_length_m - inventory_item.length) * Decimal('1000')  # mm
                        inventory_item.length = Decimal('0')  # Material depleted

                    inventory_item.save()
                    cutting_entry.total_length_used = total_cut_length_m * Decimal('1000')  # Save in mm
                    cutting_entry.save()

            messages.success(request, 'Cutting list created and inventory updated.')
            return redirect('cutting_list_dashboard')
    else:
        form = CuttingListForm()
        formset = CuttingListEntryFormSet(queryset=CuttingListEntry.objects.none())

    return render(request, 'core/cutting_list_form.html', {
        'form': form,
        'formset': formset
    })





@login_required
def cutting_list_detail(request, pk):
    cutting_list = get_object_or_404(CuttingList, pk=pk)
    return render(request, 'core/cutting_list_detail.html', {
        'cutting_list': cutting_list
    })
    
@login_required
def cutting_list_pdf_export(request, pk):
    cutting_list = get_object_or_404(CuttingList, pk=pk)

    # Pre-calculate totals
    total_used = sum(entry.total_length_used for entry in cutting_list.entries.all())
    total_waste = sum(entry.waste for entry in cutting_list.entries.all())

    # Render the HTML template
    html_string = render_to_string('core/cutting_list_pdf.html', {
        'cutting_list': cutting_list,
        'total_used': total_used,
        'total_waste': total_waste,
    })

    # Create PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()

    # Return PDF as response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"cutting_list_{cutting_list.pk}.pdf\"'
    response.write(result)
    return response

@login_required
def quote_dashboard(request):
    quotes = Quote.objects.all().order_by('-date_created')
    return render(request, 'core/quote_dashboard.html', {'quotes': quotes})


@login_required
def quote_create(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        formset = QuoteItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            quote = form.save()
            formset.instance = quote
            formset.save()
            messages.success(request, "Quote created successfully.")
            return redirect('quote_dashboard')
    else:
        form = QuoteForm()
        formset = QuoteItemFormSet()
    return render(request, 'core/quote_form.html', {'form': form, 'formset': formset})


@login_required
def quote_detail(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    return render(request, 'core/quote_detail.html', {'quote': quote})


@login_required
def quote_pdf_export(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    template = get_template('core/quote_pdf.html')
    html_content = template.render({'quote': quote})
    pdf_file = HTML(string=html_content).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Quote_{quote.pk}.pdf"'
    return response

# Calendar data endpoint
# views.py
from .models import Reminder

@login_required
def calendar_events(request):
    events = []

    # Existing Tasks, Projects, Quotes
    for task in Task.objects.all():
        events.append({
            "id": f"task-{task.id}",
            "title": f"Task: {task.name}",
            "start": task.due_date.isoformat(),
            "color": "#dc3545",  # red
            "url": f"/tasks/{task.id}/"
        })

    for project in Project.objects.all():
        events.append({
            "id": f"project-{project.id}",
            "title": f"Project: {project.name}",
            "start": project.start_date.isoformat(),
            "end": project.end_date.isoformat(),
            "color": "#198754",  # green
            "url": f"/projects/{project.id}/"
        })

    # New: Reminders
    for reminder in Reminder.objects.filter(user=request.user):
        events.append({
            "id": f"reminder-{reminder.id}",
            "title": f"🔔 {reminder.title}",
            "start": reminder.date.isoformat(),
            "color": "#0d6efd",  # blue
            "allDay": True
        })

    return JsonResponse(events, safe=False)

from django.views.decorators.csrf import csrf_exempt  # Add if not already imported

@csrf_exempt
@login_required
def add_reminder(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        reminder = Reminder.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            date=data.get('date'),
            user=request.user
        )
        return JsonResponse({'status': 'success', 'id': reminder.id})
    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
@login_required
def edit_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        reminder.title = data.get('title', reminder.title)
        reminder.description = data.get('description', reminder.description)
        reminder.date = data.get('date', reminder.date)
        reminder.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
@login_required
def delete_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == 'POST':
        reminder.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# 🚚 Shipping Views
def shipping_dashboard(request):
    incoming_shipments = Shipment.objects.filter(shipment_type='incoming').order_by('-expected_date')
    outgoing_shipments = Shipment.objects.filter(shipment_type='outgoing').order_by('-expected_date')
    return render(request, 'core/shipping_dashboard.html', {
        'incoming_shipments': incoming_shipments,
        'outgoing_shipments': outgoing_shipments
    })

@login_required
def shipment_detail(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    return render(request, 'core/shipment_detail.html', {'shipment': shipment})


@login_required
def shipment_create(request):
    if request.method == 'POST':
        form = ShipmentForm(request.POST, request.FILES)
        if form.is_valid():
            shipment = form.save()
            messages.success(request, "Shipment created successfully.")
            return redirect('shipping_dashboard')
    else:
        form = ShipmentForm()
    return render(request, 'core/shipment_form.html', {'form': form})

@login_required
def conversation_list(request):
    conversations = request.user.conversations.all()
    return render(request, 'core/conversation_list.html', {'conversations': conversations})

@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.user not in conversation.participants.all():
        return redirect('conversation_list')

    messages = conversation.messages.order_by('timestamp')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.conversation = conversation
            message.save()
            return redirect('conversation_detail', pk=pk)
    else:
        form = MessageForm()

    return render(request, 'core/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'form': form
    })
    
def chat_dashboard(request):
    chats = Chat.objects.filter(participants=request.user)
    users = User.objects.exclude(id=request.user.id)  # to list possible chat participants
    return render(request, 'chat_dashboard.html', {'chats': chats, 'users': users})

@login_required
def chat_create(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        chat_type = request.POST.get('chat_type')
        participant_ids = request.POST.getlist('participants')
        participants = User.objects.filter(id__in=participant_ids)

        if chat_type == 'private' and participants.count() == 1:
            name = f"Private chat with {participants.first().username}"
        elif chat_type == 'group' and not name:
            name = "Unnamed Group"

        chat = Chat.objects.create(name=name, chat_type=chat_type)
        chat.participants.add(*participants)
        chat.participants.add(request.user)  # add current user too
        return redirect('chat_detail', chat_id=chat.id)
    return redirect('chat_dashboard')

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return redirect('chat_dashboard')  # Prevent access if not participant

    messages = chat.messages.all().order_by('timestamp')

    if request.method == "POST":
        message_text = request.POST.get('message', '').strip()
        uploaded_file = request.FILES.get('file', None)

        if message_text or uploaded_file:
            ChatMessage.objects.create(
                chat=chat,
                sender=request.user,
                message=message_text,
                file=uploaded_file
            )
        return redirect('chat_detail', chat_id=chat.id)

    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messages': messages
    })

@login_required
def chat_room(request, room_name):
    """ Render the chat room template """
    return render(request, 'chat_room.html', {
        'room_name': room_name
    })

@csrf_exempt
def new_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            chat = Chat.objects.create(name=name, created_by=request.user)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


from .models import Invoice, InvoiceMaterial
from .forms import InvoiceForm, InvoiceMaterialFormSet

@login_required
def invoice_dashboard(request):
    invoices = Invoice.objects.all().order_by('-date_received')
    return render(request, 'core/invoice_dashboard.html', {'invoices': invoices})

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        formset = InvoiceMaterialFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            materials = formset.save(commit=False)
            for material in materials:
                material.invoice = invoice
                material.save()

                # 🔥 Update inventory if it's for Materials
                if invoice.category == 'MATERIALS' and material.material:
                    material.material.length += material.quantity
                    material.material.save()

            messages.success(request, "Invoice and materials added successfully.")
            return redirect('invoice_dashboard')
    else:
        form = InvoiceForm()
        formset = InvoiceMaterialFormSet(queryset=InvoiceMaterial.objects.none())

    return render(request, 'core/invoice_form.html', {'form': form, 'formset': formset})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'core/invoice_detail.html', {'invoice': invoice})


from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from .models import Invoice, Task, InventoryItem, User


@login_required
def stats_dashboard(request):
    # Incomes
    total_income = sum(invoice.materials.aggregate(total=models.Sum('quantity'))['total'] or 0 for invoice in Invoice.objects.all())

    # Expenses
    total_expenses = ProductionCost.objects.aggregate(total=models.Sum('amount'))['total'] or 0

    # Material shortages (quantity < 10 for demo)
    shortages = InventoryItem.objects.filter(quantity__lt=10)

    # Task stats
    task_counts = {
        'pending': Task.objects.filter(status='Pending').count(),
        'in_progress': Task.objects.filter(status='In Progress').count(),
        'completed': Task.objects.filter(status='Completed').count(),
    }

    # Worker efficiency (tasks completed per user)
    worker_efficiency = User.objects.annotate(completed_tasks=models.Count('assigned_tasks', filter=models.Q(assigned_tasks__status='Completed')))

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'shortages': shortages,
        'task_counts': task_counts,
        'worker_efficiency': worker_efficiency,
    }
    return render(request, 'stats_dashboard.html', context)
from .models import UserRole
@login_required
def user_list(request):
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()   # '', 'active', 'inactive'
    staff = request.GET.get('staff', '').strip()     # '', 'yes', 'no'

    users = User.objects.all().order_by('username')

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)

    if staff == 'yes':
        users = users.filter(is_staff=True)
    elif staff == 'no':
        users = users.filter(is_staff=False)

    # Attach safe role string for template
    for u in users:
        try:
            ur = u.userrole
            role_display = ur.get_role_display() if hasattr(ur, "get_role_display") else (ur.role or "")
        except Exception:
            role_display = ""
        u.role_display = role_display

    # Provide role choices to the template (value, label)
    role_choices = UserRole._meta.get_field('role').choices

    return render(request, "core/user_list.html", {
        "users": users,
        "q": q, "status": status, "staff": staff,
        "role_choices": role_choices,
    })
    
@login_required
def assign_role(request):
    if request.method != "POST":
        return redirect('user_list')

    role = (request.POST.get('role') or '').strip()
    ids = request.POST.getlist('user_ids') or request.POST.getlist('user_ids[]')

    # Validate role against choices
    valid_roles = [c[0] for c in UserRole._meta.get_field('role').choices]
    if role not in valid_roles:
        messages.error(request, "Invalid role selected.")
        return redirect('user_list')

    if not ids:
        messages.warning(request, "No users selected.")
        return redirect('user_list')

    updated = 0
    for uid in ids:
        try:
            u = User.objects.get(pk=uid)
        except User.DoesNotExist:
            continue
        ur, _created = UserRole.objects.get_or_create(user=u)
        ur.role = role
        ur.save()
        updated += 1

    label = dict(UserRole._meta.get_field('role').choices).get(role, role)
    messages.success(request, f"Assigned role “{label}” to {updated} user(s).")
    return redirect('user_list')
    