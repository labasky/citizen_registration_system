# Authentication and Access Control Implementation

## 1. Overview

This document outlines the implementation details for the authentication and access control system of the Citizen Registration System. The system will provide secure user authentication, role-based access control, and comprehensive audit logging to ensure data security and integrity.

## 2. Authentication System

### 2.1 User Authentication Flow

1. User navigates to the login page
2. User enters username/email and password
3. System validates credentials against the database
4. If valid, a session is created and user is redirected to appropriate dashboard
5. If invalid, error message is displayed and login attempt is logged
6. After a configurable number of failed attempts, account is temporarily locked

### 2.2 Password Security

- Passwords will be stored using bcrypt hashing algorithm with salt
- Minimum password requirements:
  - At least 8 characters long
  - Must contain at least one uppercase letter
  - Must contain at least one lowercase letter
  - Must contain at least one number
  - Must contain at least one special character
- Password expiry after 90 days
- Prevention of password reuse (last 5 passwords)
- Secure password reset mechanism with time-limited tokens

### 2.3 Session Management

- JWT (JSON Web Tokens) for session management
- Token expiration after 30 minutes of inactivity
- Secure cookie storage with HttpOnly and Secure flags
- CSRF protection with anti-forgery tokens
- Session invalidation on logout or password change

## 3. Role-Based Access Control (RBAC)

### 3.1 User Roles

| Role | Description | Access Level |
|------|-------------|--------------|
| Super Administrator | System-wide administration | Full system access |
| State Administrator | State-level administration | Full access to state data |
| LGA Administrator | LGA-level administration | Full access to LGA data |
| Data Entry Operator | Data entry and basic operations | Limited to assigned functions |
| Report Viewer | View reports and analytics | Read-only access to reports |

### 3.2 Permission Matrix

| Permission | Super Admin | State Admin | LGA Admin | Data Entry | Report Viewer |
|------------|-------------|-------------|-----------|------------|---------------|
| manage_users | ✓ | ✓ (state only) | ✓ (LGA only) | ✗ | ✗ |
| manage_roles | ✓ | ✗ | ✗ | ✗ | ✗ |
| register_citizens | ✓ | ✓ | ✓ | ✓ | ✗ |
| edit_citizens | ✓ | ✓ | ✓ | ✓ | ✗ |
| view_citizens | ✓ | ✓ | ✓ | ✓ | ✓ |
| delete_citizens | ✓ | ✓ | ✗ | ✗ | ✗ |
| print_id_cards | ✓ | ✓ | ✓ | ✓ | ✗ |
| generate_reports | ✓ | ✓ | ✓ | ✗ | ✓ |
| export_data | ✓ | ✓ | ✓ | ✗ | ✓ |
| manage_system | ✓ | ✗ | ✗ | ✗ | ✗ |

### 3.3 Access Control Implementation

- Permission checks at both frontend and backend
- UI elements dynamically shown/hidden based on permissions
- API endpoints protected with permission middleware
- Database-level row security policies for data isolation

## 4. Implementation Details

### 4.1 Backend Authentication Implementation (Python/Django)

```python
# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, username, password, **extra_fields)

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('role', 'permission')
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, blank=True)
    lga = models.ForeignKey('LocalGovernmentArea', on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey('Ward', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_permission(self, permission_name):
        if not self.role:
            return False
        return RolePermission.objects.filter(
            role=self.role,
            permission__name=permission_name
        ).exists()
    
    def has_jurisdiction(self, state_id=None, lga_id=None, ward_id=None):
        # Super admin has access to everything
        if self.role.name == 'Super Administrator':
            return True
        
        # State admin has access to their state and all LGAs/wards within
        if self.role.name == 'State Administrator':
            if state_id and self.state_id != state_id:
                return False
            return True
        
        # LGA admin has access to their LGA and all wards within
        if self.role.name == 'LGA Administrator':
            if state_id and self.state_id != state_id:
                return False
            if lga_id and self.lga_id != lga_id:
                return False
            return True
        
        # Data entry operator has access to their assigned ward only
        if self.role.name == 'Data Entry Operator':
            if state_id and self.state_id != state_id:
                return False
            if lga_id and self.lga_id != lga_id:
                return False
            if ward_id and self.ward_id != ward_id:
                return False
            return True
        
        return False

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
```

### 4.2 Authentication Views and Serializers

```python
# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Role, Permission, RolePermission

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email', '')
        password = data.get('password', '')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.', code='authorization')
            
            if user.locked_until and user.locked_until > timezone.now():
                raise serializers.ValidationError('Account is temporarily locked. Please try again later.', code='authorization')
            
            data['user'] = user
            return data
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value
    
    def validate_new_password(self, value):
        validate_password(value)
        return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'role', 'state', 'lga', 'ward', 'is_active')
        read_only_fields = ('id',)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'
```

### 4.3 Authentication Views

```python
# views.py
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.conf import settings
from .models import User, AuditLog
from .serializers import LoginSerializer, PasswordChangeSerializer, UserSerializer

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
```

### 4.4 Permission Middleware

```python
# middleware.py
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
        url_name = resolve(request.path_info).url_name
        
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
                from .models import Citizen
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
```

### 4.5 Frontend Authentication Implementation (React/Redux)

```javascript
// authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../services/authService';

// Get user from localStorage
const user = JSON.parse(localStorage.getItem('user'));

const initialState = {
  user: user ? user : null,
  isLoading: false,
  isSuccess: false,
  isError: false,
  message: '',
};

// Login user
export const login = createAsyncThunk('auth/login', async (userData, thunkAPI) => {
  try {
    return await authService.login(userData);
  } catch (error) {
    const message = error.response?.data?.message || error.message || error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

// Logout user
export const logout = createAsyncThunk('auth/logout', async (_, thunkAPI) => {
  try {
    return await authService.logout();
  } catch (error) {
    const message = error.response?.data?.message || error.message || error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

// Change password
export const changePassword = createAsyncThunk('auth/changePassword', async (passwordData, thunkAPI) => {
  try {
    return await authService.changePassword(passwordData);
  } catch (error) {
    const message = error.response?.data?.message || error.message || error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    reset: (state) => {
      state.isLoading = false;
      state.isSuccess = false;
      state.isError = false;
      state.message = '';
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isSuccess = true;
        state.user = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.isError = true;
        state.message = action.payload;
        state.user = null;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
      })
      .addCase(changePassword.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(changePassword.fulfilled, (state) => {
        state.isLoading = false;
        state.isSuccess = true;
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.isLoading = false;
        state.isError = true;
        state.message = action.payload;
      });
  },
});

export const { reset } = authSlice.actions;
export default authSlice.reducer;
```

```javascript
// authService.js
import axios from 'axios';

const API_URL = '/api/auth/';

// Login user
const login = async (userData) => {
  const response = await axios.post(API_URL + 'login/', userData);
  
  if (response.data) {
    localStorage.setItem('user', JSON.stringify(response.data));
    localStorage.setItem('token', response.data.access);
    localStorage.setItem('refreshToken', response.data.refresh);
  }
  
  return response.data;
};

// Logout user
const logout = async () => {
  const refreshToken = localStorage.getItem('refreshToken');
  
  if (refreshToken) {
    try {
      await axios.post(API_URL + 'logout/', { refresh: refreshToken }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
};

// Change password
const changePassword = async (passwordData) => {
  const response = await axios.post(API_URL + 'password/change/', passwordData, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });
  
  return response.data;
};

const authService = {
  login,
  logout,
  changePassword,
};

export default authService;
```

```javascript
// axiosConfig.js
import axios from 'axios';

// Add a request interceptor
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is 401 and hasn't already been retried
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post('/api/auth/token/refresh/', {
          refresh: refreshToken,
        });
        
        const { access } = response.data;
        
        // Update the token in localStorage
        localStorage.setItem('token', access);
        
        // Update the Authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        
        // Retry the original request
        return axios(originalRequest);
      } catch (refreshError) {
        // If refresh token is invalid, logout the user
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        
        // Redirect to login page
        window.location.href = '/login';
        
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default axios;
```

### 4.6 Permission Utility for Frontend

```javascript
// permissionUtils.js
/**
 * Check if the user has a specific permission
 * @param {Object} user - The user object from Redux store
 * @param {String} permission - The permission to check
 * @returns {Boolean} - Whether the user has the permission
 */
export const hasPermission = (user, permission) => {
  if (!user || !user.role || !user.role.permissions) {
    return false;
  }
  
  return user.role.permissions.includes(permission);
};

/**
 * Check if the user has jurisdiction over a specific location
 * @param {Object} user - The user object from Redux store
 * @param {Number} stateId - The state ID to check
 * @param {Number} lgaId - The LGA ID to check
 * @param {Number} wardId - The ward ID to check
 * @returns {Boolean} - Whether the user has jurisdiction
 */
export const hasJurisdiction = (user, stateId, lgaId, wardId) => {
  if (!user || !user.role) {
    return false;
  }
  
  // Super admin has access to everything
  if (user.role.name === 'Super Administrator') {
    return true;
  }
  
  // State admin has access to their state and all LGAs/wards within
  if (user.role.name === 'State Administrator') {
    if (stateId && user.state.id !== stateId) {
      return false;
    }
    return true;
  }
  
  // LGA admin has access to their LGA and all wards within
  if (user.role.name === 'LGA Administrator') {
    if (stateId && user.state.id !== stateId) {
      return false;
    }
    if (lgaId && user.lga.id !== lgaId) {
      return false;
    }
    return true;
  }
  
  // Data entry operator has access to their assigned ward only
  if (user.role.name === 'Data Entry Operator') {
    if (stateId && user.state.id !== stateId) {
      return false;
    }
    if (lgaId && user.lga.id !== lgaId) {
      return false;
    }
    if (wardId && user.ward.id !== wardId) {
      return false;
    }
    return true;
  }
  
  return false;
};

/**
 * Higher-order component to protect routes based on permissions
 * @param {Component} Component - The component to render if authorized
 * @param {String} permission - The required permission
 * @returns {Component} - The protected component
 */
export const withPermission = (Component, permission) => {
  return (props) => {
    const { user } = useSelector((state) => state.auth);
    
    if (!hasPermission(user, permission)) {
      return <Redirect to="/unauthorized" />;
    }
    
    return <Component {...props} />;
  };
};
```

### 4.7 Login Component

```jsx
// Login.jsx
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { login, reset } from '../features/auth/authSlice';
import { toast } from 'react-toastify';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  
  const { email, password } = formData;
  
  const dispatch = useDispatch();
  const history = useHistory();
  
  const { user, isLoading, isSuccess, isError, message } = useSelector((state) => state.auth);
  
  useEffect(() => {
    if (isError) {
      toast.error(message);
    }
    
    // Redirect when logged in
    if (isSuccess || user) {
      history.push('/dashboard');
    }
    
    dispatch(reset());
  }, [isError, isSuccess, user, message, history, dispatch]);
  
  const onChange = (e) => {
    setFormData((prevState) => ({
      ...prevState,
      [e.target.name]: e.target.value,
    }));
  };
  
  const onSubmit = (e) => {
    e.preventDefault();
    
    const userData = {
      email,
      password,
    };
    
    dispatch(login(userData));
  };
  
  return (
    <div className="login-container">
      <img src="/logo.svg" alt="Nigerian Coat of Arms" className="logo" />
      <h1>CITIZEN REGISTRATION SYSTEM</h1>
      
      <form onSubmit={onSubmit}>
        <div className="input-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            value={email}
            onChange={onChange}
            placeholder="Enter your email"
            required
          />
        </div>
        
        <div className="input-group">
          <label htmlFor="password">Password</label>
          <div className="password-container">
            <input
              type="password"
              id="password"
              name="password"
              value={password}
              onChange={onChange}
              placeholder="Enter your password"
              required
            />
            <span className="password-toggle" onClick={() => {
              const passwordInput = document.getElementById('password');
              if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
              } else {
                passwordInput.type = 'password';
              }
            }}>👁️</span>
          </div>
        </div>
        
        <div className="remember-forgot">
          <div className="remember-me">
            <input type="checkbox" id="remember" name="remember" />
            <label htmlFor="remember">Remember me</label>
          </div>
          <a href="/forgot-password" className="forgot-password">Forgot Password?</a>
        </div>
        
        <button type="submit" className="login-button" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'LOGIN'}
        </button>
      </form>
      
      <div className="footer">
        © 2025 State Government of Nigeria<br />
        Version 1.0
      </div>
    </div>
  );
};

export default Login;
```

## 5. Security Considerations

### 5.1 Protection Against Common Vulnerabilities

- **SQL Injection**: Use parameterized queries and ORM
- **Cross-Site Scripting (XSS)**: Sanitize user inputs, use React's built-in XSS protection
- **Cross-Site Request Forgery (CSRF)**: Implement anti-forgery tokens
- **Broken Authentication**: Implement account lockout, secure password policies
- **Sensitive Data Exposure**: Use HTTPS, encrypt sensitive data
- **Security Misconfiguration**: Follow security best practices, regular security audits
- **Insecure Deserialization**: Validate all inputs, use safe deserialization methods
- **Using Components with Known Vulnerabilities**: Regular dependency updates
- **Insufficient Logging & Monitoring**: Comprehensive audit logging

### 5.2 Audit Logging

All security-relevant events will be logged, including:

- Login attempts (successful and failed)
- Password changes
- User creation, modification, and deletion
- Role and permission changes
- Access to sensitive data
- Data modification operations

Logs will include:
- Timestamp
- User ID
- Action performed
- Affected entity
- IP address
- Additional details when relevant

### 5.3 Regular Security Reviews

- Scheduled security audits every 6 months
- Penetration testing before major releases
- Code reviews with security focus
- Regular dependency vulnerability scanning

## 6. Implementation Plan

### 6.1 Phase 1: Core Authentication

1. Implement user model and authentication backend
2. Create login, logout, and password change functionality
3. Implement JWT token handling
4. Set up basic permission structure
5. Create audit logging system

### 6.2 Phase 2: Access Control

1. Implement role and permission models
2. Create role-permission assignments
3. Implement permission checking middleware
4. Add jurisdiction-based access control
5. Integrate with frontend components

### 6.3 Phase 3: Security Enhancements

1. Implement account lockout mechanism
2. Add password complexity requirements
3. Set up password expiry and history
4. Enhance audit logging
5. Implement security monitoring

## 7. Testing Strategy

### 7.1 Unit Testing

- Test authentication functions
- Test permission checks
- Test jurisdiction validation
- Test password policies

### 7.2 Integration Testing

- Test authentication flow
- Test role-based access control
- Test API endpoint security
- Test token refresh mechanism

### 7.3 Security Testing

- Test against OWASP Top 10 vulnerabilities
- Perform penetration testing
- Test account lockout mechanism
- Test audit logging accuracy
