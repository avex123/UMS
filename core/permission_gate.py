# core/permission_gate.py
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import resolve

class PermissionGateMiddleware:
    """
    Enforces Django model permissions per-view using URL names.
    Example mapping in settings:
        PERMISSION_VIEW_MAP = {
            "project_create": ["core.add_project"],
            "project_list":   ["core.view_project"],
            # also supports per-method maps:
            "task_detail": {"POST": ["core.change_task"], "*": ["core.view_task"]},
        }
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check for authenticated, non-superusers
        if request.user.is_authenticated and not request.user.is_superuser:
            try:
                match = resolve(request.path_info)
                view_name = match.view_name or ""
            except Exception:
                view_name = ""

            perm_map = getattr(settings, "PERMISSION_VIEW_MAP", {})
            required = perm_map.get(view_name)

            if required:
                # allow dict like {"POST": [...], "*": [...]}
                if isinstance(required, dict):
                    required = required.get(request.method, required.get("*", []))

                if required and not request.user.has_perms(required):
                    raise PermissionDenied

        return self.get_response(request)
