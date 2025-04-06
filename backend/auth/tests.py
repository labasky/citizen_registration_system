import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from auth.models import Role, Permission, UserRole
import json

class AuthModelsTestCase(TestCase):
    """
    Test cases for authentication and authorization models
    """
    
    def setUp(self):
        """
        Set up test data
        """
        # Create test permissions
        self.view_citizens_perm = Permission.objects.create(
            name='view_citizens',
            description='Can view citizens'
        )
        
        self.add_citizens_perm = Permission.objects.create(
            name='add_citizens',
            description='Can add citizens'
        )
        
        self.edit_citizens_perm = Permission.objects.create(
            name='edit_citizens',
            description='Can edit citizens'
        )
        
        self.generate_reports_perm = Permission.objects.create(
            name='generate_reports',
            description='Can generate reports'
        )
        
        # Create test roles
        self.admin_role = Role.objects.create(
            name='Administrator',
            description='System administrator'
        )
        
        self.data_entry_role = Role.objects.create(
            name='Data Entry',
            description='Data entry staff'
        )
        
        self.report_viewer_role = Role.objects.create(
            name='Report Viewer',
            description='Report viewer'
        )
        
        # Assign permissions to roles
        self.admin_role.permissions.add(
            self.view_citizens_perm,
            self.add_citizens_perm,
            self.edit_citizens_perm,
            self.generate_reports_perm
        )
        
        self.data_entry_role.permissions.add(
            self.view_citizens_perm,
            self.add_citizens_perm
        )
        
        self.report_viewer_role.permissions.add(
            self.view_citizens_perm,
            self.generate_reports_perm
        )
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        self.data_entry_user = User.objects.create_user(
            username='dataentry',
            email='dataentry@example.com',
            password='dataentrypassword'
        )
        
        self.report_viewer_user = User.objects.create_user(
            username='reportviewer',
            email='reportviewer@example.com',
            password='reportviewerpassword'
        )
        
        # Assign roles to users
        UserRole.objects.create(
            user=self.admin_user,
            role=self.admin_role,
            state_id=None,  # Admin has access to all states
            lga_id=None     # Admin has access to all LGAs
        )
        
        UserRole.objects.create(
            user=self.data_entry_user,
            role=self.data_entry_role,
            state_id=1,     # Data entry user has access to state 1
            lga_id=1        # Data entry user has access to LGA 1
        )
        
        UserRole.objects.create(
            user=self.report_viewer_user,
            role=self.report_viewer_role,
            state_id=1,     # Report viewer has access to state 1
            lga_id=None     # Report viewer has access to all LGAs in state 1
        )
    
    def test_role_permissions(self):
        """
        Test role permissions
        """
        # Test admin role permissions
        self.assertTrue(self.admin_role.has_permission('view_citizens'))
        self.assertTrue(self.admin_role.has_permission('add_citizens'))
        self.assertTrue(self.admin_role.has_permission('edit_citizens'))
        self.assertTrue(self.admin_role.has_permission('generate_reports'))
        
        # Test data entry role permissions
        self.assertTrue(self.data_entry_role.has_permission('view_citizens'))
        self.assertTrue(self.data_entry_role.has_permission('add_citizens'))
        self.assertFalse(self.data_entry_role.has_permission('edit_citizens'))
        self.assertFalse(self.data_entry_role.has_permission('generate_reports'))
        
        # Test report viewer role permissions
        self.assertTrue(self.report_viewer_role.has_permission('view_citizens'))
        self.assertFalse(self.report_viewer_role.has_permission('add_citizens'))
        self.assertFalse(self.report_viewer_role.has_permission('edit_citizens'))
        self.assertTrue(self.report_viewer_role.has_permission('generate_reports'))
    
    def test_user_roles(self):
        """
        Test user roles
        """
        # Test admin user role
        admin_user_role = UserRole.objects.get(user=self.admin_user)
        self.assertEqual(admin_user_role.role, self.admin_role)
        self.assertIsNone(admin_user_role.state_id)
        self.assertIsNone(admin_user_role.lga_id)
        
        # Test data entry user role
        data_entry_user_role = UserRole.objects.get(user=self.data_entry_user)
        self.assertEqual(data_entry_user_role.role, self.data_entry_role)
        self.assertEqual(data_entry_user_role.state_id, 1)
        self.assertEqual(data_entry_user_role.lga_id, 1)
        
        # Test report viewer user role
        report_viewer_user_role = UserRole.objects.get(user=self.report_viewer_user)
        self.assertEqual(report_viewer_user_role.role, self.report_viewer_role)
        self.assertEqual(report_viewer_user_role.state_id, 1)
        self.assertIsNone(report_viewer_user_role.lga_id)
    
    def test_user_permissions(self):
        """
        Test user permissions
        """
        # Test admin user permissions
        self.assertTrue(self.admin_user.has_perm('view_citizens'))
        self.assertTrue(self.admin_user.has_perm('add_citizens'))
        self.assertTrue(self.admin_user.has_perm('edit_citizens'))
        self.assertTrue(self.admin_user.has_perm('generate_reports'))
        
        # Test data entry user permissions
        self.assertTrue(self.data_entry_user.has_perm('view_citizens'))
        self.assertTrue(self.data_entry_user.has_perm('add_citizens'))
        self.assertFalse(self.data_entry_user.has_perm('edit_citizens'))
        self.assertFalse(self.data_entry_user.has_perm('generate_reports'))
        
        # Test report viewer user permissions
        self.assertTrue(self.report_viewer_user.has_perm('view_citizens'))
        self.assertFalse(self.report_viewer_user.has_perm('add_citizens'))
        self.assertFalse(self.report_viewer_user.has_perm('edit_citizens'))
        self.assertTrue(self.report_viewer_user.has_perm('generate_reports'))
    
    def test_user_jurisdiction(self):
        """
        Test user jurisdiction
        """
        # Test admin user jurisdiction (all states and LGAs)
        admin_user_role = UserRole.objects.get(user=self.admin_user)
        self.assertTrue(admin_user_role.has_jurisdiction(state_id=1, lga_id=1))
        self.assertTrue(admin_user_role.has_jurisdiction(state_id=2, lga_id=2))
        
        # Test data entry user jurisdiction (only state 1, LGA 1)
        data_entry_user_role = UserRole.objects.get(user=self.data_entry_user)
        self.assertTrue(data_entry_user_role.has_jurisdiction(state_id=1, lga_id=1))
        self.assertFalse(data_entry_user_role.has_jurisdiction(state_id=1, lga_id=2))
        self.assertFalse(data_entry_user_role.has_jurisdiction(state_id=2, lga_id=1))
        
        # Test report viewer user jurisdiction (all LGAs in state 1)
        report_viewer_user_role = UserRole.objects.get(user=self.report_viewer_user)
        self.assertTrue(report_viewer_user_role.has_jurisdiction(state_id=1, lga_id=1))
        self.assertTrue(report_viewer_user_role.has_jurisdiction(state_id=1, lga_id=2))
        self.assertFalse(report_viewer_user_role.has_jurisdiction(state_id=2, lga_id=1))


class AuthAPITestCase(TestCase):
    """
    Test cases for authentication API endpoints
    """
    
    def setUp(self):
        """
        Set up test data and client
        """
        # Create test roles
        self.admin_role = Role.objects.create(
            name='Administrator',
            description='System administrator'
        )
        
        self.data_entry_role = Role.objects.create(
            name='Data Entry',
            description='Data entry staff'
        )
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        self.data_entry_user = User.objects.create_user(
            username='dataentry',
            email='dataentry@example.com',
            password='dataentrypassword'
        )
        
        # Assign roles to users
        UserRole.objects.create(
            user=self.admin_user,
            role=self.admin_role,
            state_id=None,
            lga_id=None
        )
        
        UserRole.objects.create(
            user=self.data_entry_user,
            role=self.data_entry_role,
            state_id=1,
            lga_id=1
        )
        
        # Create API client
        self.client = APIClient()
    
    def test_login_api(self):
        """
        Test login API endpoint
        """
        url = reverse('auth-login')
        
        # Test valid login
        response = self.client.post(url, {
            'username': 'admin',
            'password': 'adminpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'admin')
        self.assertEqual(response.data['user']['role'], 'Administrator')
        
        # Test invalid login
        response = self.client.post(url, {
            'username': 'admin',
            'password': 'wrongpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_api(self):
        """
        Test logout API endpoint
        """
        # Login first
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('auth-logout')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Successfully logged out')
    
    def test_user_profile_api(self):
        """
        Test user profile API endpoint
        """
        url = reverse('auth-profile')
        
        # Test authenticated access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'admin')
        self.assertEqual(response.data['email'], 'admin@example.com')
        self.assertEqual(response.data['role'], 'Administrator')
        
        # Test unauthenticated access
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_change_password_api(self):
        """
        Test change password API endpoint
        """
        url = reverse('auth-change-password')
        
        # Test authenticated access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, {
            'old_password': 'adminpassword',
            'new_password': 'newadminpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Password changed successfully')
        
        # Verify password change
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.check_password('newadminpassword'))
        
        # Test with incorrect old password
        response = self.client.post(url, {
            'old_password': 'adminpassword',  # Old password, now incorrect
            'new_password': 'anothernewpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test unauthenticated access
        self.client.force_authenticate(user=None)
        response = self.client.post(url, {
            'old_password': 'newadminpassword',
            'new_password': 'anothernewpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


if __name__ == '__main__':
    unittest.main()
