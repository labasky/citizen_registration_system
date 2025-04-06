// backend/auth/views.py
from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import User, Role, Permission, RolePermission, AuditLog
from .serializers import (
    LoginSerializer, PasswordChangeSerializer, UserSerializer, 
    RoleSerializer, PermissionSerializer, RolePermissionSerializer,
    UserCreateSerializer, PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer
)

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Reset failed login attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = timezone.now()
            user.save()
            
            # Create tokens
            refresh = RefreshToken.for_user(user)
            
            # Log successful login
            AuditLog.objects.create(
                user=user,
                action='login',
                entity_type='user',
                entity_id=user.id,
                ip_address=self.get_client_ip(request),
                details='Successful login'
            )
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        else:
            # Handle failed login attempt
            email = request.data.get('email', '')
            try:
                user = User.objects.get(email=email)
                user.failed_login_attempts += 1
                
                # Lock account after X failed attempts
                if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                    user.locked_until = timezone.now() + timezone.timedelta(minutes=settings.ACCOUNT_LOCKOUT_DURATION)
                
                user.save()
                
                # Log failed login
                AuditLog.objects.create(
                    user=user,
                    action='login_failed',
                    entity_type='user',
                    entity_id=user.id,
                    ip_address=self.get_client_ip(request),
                    details=f'Failed login attempt ({user.failed_login_attempts})'
                )
            except User.DoesNotExist:
                # Log unknown user login attempt
                AuditLog.objects.create(
                    user=None,
                    action='login_failed',
                    entity_type='user',
                    entity_id=None,
                    ip_address=self.get_client_ip(request),
                    details=f'Failed login attempt for unknown user: {email}'
                )
            
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        try:
            # Log logout
            AuditLog.objects.create(
                user=request.user,
                action='logout',
                entity_type='user',
                entity_id=request.user.id,
                ip_address=self.get_client_ip(request),
                details='User logged out'
            )
            
            # Blacklist the token
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class PasswordChangeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.password_changed_at = timezone.now()
            user.save()
            
            # Log password change
            AuditLog.objects.create(
                user=user,
                action='password_change',
                entity_type='user',
                entity_id=user.id,
                ip_address=self.get_client_ip(request),
                details='Password changed'
            )
            
            return Response({'detail': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class PasswordResetRequestView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Generate token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Send email
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                subject = "Password Reset Request"
                message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                    'valid_hours': settings.PASSWORD_RESET_TIMEOUT // 3600
                })
                
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                
                # Log password reset request
                AuditLog.objects.create(
                    user=user,
                    action='password_reset_request',
                    entity_type='user',
                    entity_id=user.id,
                    ip_address=self.get_client_ip(request),
                    details='Password reset requested'
                )
                
                return Response({'detail': 'Password reset email has been sent.'})
            except User.DoesNotExist:
                # Don't reveal that the user doesn't exist
                return Response({'detail': 'Password reset email has been sent.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class PasswordResetConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['password'])
                    user.password_changed_at = timezone.now()
                    user.save()
                    
                    # Log password reset
                    AuditLog.objects.create(
                        user=user,
                        action='password_reset',
                        entity_type='user',
                        entity_id=user.id,
                        ip_address=self.get_client_ip(request),
                        details='Password reset completed'
                    )
                    
                    return Response({'detail': 'Password has been reset successfully.'})
                else:
                    return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Super admin can see all users
        if user.role.name == 'Super Administrator':
            return User.objects.all()
        
        # State admin can see users in their state
        if user.role.name == 'State Administrator':
            return User.objects.filter(state=user.state)
        
        # LGA admin can see users in their LGA
        if user.role.name == 'LGA Administrator':
            return User.objects.filter(state=user.state, lga=user.lga)
        
        # Data entry operator can only see themselves
        return User.objects.filter(id=user.id)
    
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Log user creation
        AuditLog.objects.create(
            user=self.request.user,
            action='user_create',
            entity_type='user',
            entity_id=user.id,
            ip_address=self.get_client_ip(self.request),
            details=f'Created user: {user.email}'
        )
    
    def perform_update(self, serializer):
        user = serializer.save()
        
        # Log user update
        AuditLog.objects.create(
            user=self.request.user,
            action='user_update',
            entity_type='user',
            entity_id=user.id,
            ip_address=self.get_client_ip(self.request),
            details=f'Updated user: {user.email}'
        )
    
    def perform_destroy(self, instance):
        # Log user deletion
        AuditLog.objects.create(
            user=self.request.user,
            action='user_delete',
            entity_type='user',
            entity_id=instance.id,
            ip_address=self.get_client_ip(self.request),
            details=f'Deleted user: {instance.email}'
        )
        
        instance.delete()
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Only super admin can manage roles
        if user.has_permission('manage_roles'):
            return Role.objects.all()
        
        # Others can only view roles
        return Role.objects.none()

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Only super admin can view all permissions
        if user.has_permission('manage_roles'):
            return Permission.objects.all()
        
        return Permission.objects.none()

class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Only super admin can manage role permissions
        if user.has_permission('manage_roles'):
            return RolePermission.objects.all()
        
        return RolePermission.objects.none()
    
    def perform_create(self, serializer):
        role_permission = serializer.save()
        
        # Log role permission creation
        AuditLog.objects.create(
            user=self.request.user,
            action='role_permission_create',
            entity_type='role_permission',
            entity_id=role_permission.id,
            ip_address=self.get_client_ip(self.request),
            details=f'Added permission {role_permission.permission.name} to role {role_permission.role.name}'
        )
    
    def perform_destroy(self, instance):
        # Log role permission deletion
        AuditLog.objects.create(
            user=self.request.user,
            action='role_permission_delete',
            entity_type='role_permission',
            entity_id=instance.id,
            ip_address=self.get_client_ip(self.request),
            details=f'Removed permission {instance.permission.name} from role {instance.role.name}'
        )
        
        instance.delete()
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
