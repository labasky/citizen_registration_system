// backend/auth/middleware.py
from django.http import HttpResponseForbidden
from django.urls import resolve
from .models import User

class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define URL patterns and required permissions
        self.url_permissions = {
            'citizen-list': 'view_citizens',
            'citizen-create': 'register_citizens',
            'citizen-detail': 'view_citizens',
            'citizen-update': 'edit_citizens',
            'citizen-delete': 'delete_citizens',
            'id-card-generate': 'print_id_cards',
            'report-list': 'generate_reports',
            'report-detail': 'generate_reports',
            'export-data': 'export_data',
            'user-list': 'manage_users',
            'user-create': 'manage_users',
            'user-detail': 'manage_users',
            'user-update': 'manage_users',
            'role-list': 'manage_roles',
            'role-detail': 'manage_roles',
            'system-settings': 'manage_system',
        }
    
    def __call__(self, request):
        # Skip permission check for authentication endpoints
        if request.path.startswith('/api/auth/'):
            return self.get_response(request)
        
        # Skip permission check if user is not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Get the URL name
        try:
            url_name = resolve(request.path_info).url_name
        except:
            # If URL can't be resolved, allow the request to continue
            return self.get_response(request)
        
        # Check if URL requires permission
        if url_name in self.url_permissions:
            required_permission = self.url_permissions[url_name]
            
            # Check if user has the required permission
            if not request.user.has_permission(required_permission):
                return HttpResponseForbidden("You don't have permission to access this resource")
        
        # Check jurisdiction for citizen data
        if url_name in ['citizen-detail', 'citizen-update', 'citizen-delete']:
            citizen_id = resolve(request.path_info).kwargs.get('pk')
            if citizen_id:
                from citizen.models import Citizen
                try:
                    citizen = Citizen.objects.get(pk=citizen_id)
                    if not request.user.has_jurisdiction(
                        state_id=citizen.residence_state_id,
                        lga_id=citizen.residence_lga_id,
                        ward_id=citizen.residence_ward_id
                    ):
                        return HttpResponseForbidden("You don't have jurisdiction to access this citizen's data")
                except Citizen.DoesNotExist:
                    pass
        
        return self.get_response(request)
