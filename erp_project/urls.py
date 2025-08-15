from django.contrib import admin
from django.urls import path, include
from django.conf import settings                  # ✅ ADD THIS LINE
from django.conf.urls.static import static
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # This line connects URLs from the 'core' app
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# Custom 403 handler
def permission_denied_view(request, exception=None):
    # If the middleware attached “denied_perms”, pass them to the template
    ctx = {"denied_perms": getattr(request, "denied_perms", None)}
    return render(request, "403.html", ctx, status=403)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

# Register handler *after* urlpatterns
handler403 = "erp_project.urls.permission_denied_view"    