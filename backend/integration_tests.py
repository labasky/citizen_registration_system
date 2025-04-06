import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json

class IntegrationTestCase(TestCase):
    """
    Integration tests for the citizen registration system
    """
    
    def setUp(self):
        """
        Set up test data and client
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test client
        self.client = Client()
    
    def test_complete_registration_workflow(self):
        """
        Test the complete citizen registration workflow
        """
        # Step 1: Login
        login_url = reverse('auth-login')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        login_response = self.client.post(
            login_url, 
            json.dumps(login_data), 
            content_type='application/json'
        )
        
        self.assertEqual(login_response.status_code, 200)
        login_content = json.loads(login_response.content)
        self.assertIn('token', login_content)
        
        # Extract token for subsequent requests
        token = login_content['token']
        
        # Step 2: Register a new citizen
        register_url = reverse('citizen-list')
        citizen_data = {
            'first_name': 'Integration',
            'last_name': 'Test',
            'gender': 'Male',
            'date_of_birth': '1990-01-01',
            'phone_number': '08012345678',
            'email': 'integration.test@example.com',
            'address': '123 Integration St',
            'residence_state_id': 1,
            'residence_lga_id': 1,
            'residence_ward_id': 1,
            'occupation': {
                'sector': 'Technology',
                'employment_status': 'Employed',
                'income_level': 'Middle',
                'qualification': 'Bachelor'
            },
            'education': {
                'level': 'University',
                'institution': 'Test University',
                'year_completed': 2015
            },
            'health': {
                'blood_group': 'O+',
                'condition': 'None',
                'disability': 'None',
                'immunization_status': 'Complete'
            },
            'family': {
                'marital_status': 'Single',
                'household_size': 1,
                'children_count': 0,
                'family_type': 'Nuclear'
            }
        }
        
        register_response = self.client.post(
            register_url,
            json.dumps(citizen_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(register_response.status_code, 201)
        register_content = json.loads(register_response.content)
        self.assertIn('citizen_id', register_content)
        
        # Extract citizen ID and database ID
        citizen_id = register_content['citizen_id']
        db_id = register_content['id']
        
        # Step 3: Retrieve the registered citizen
        retrieve_url = reverse('citizen-detail', args=[db_id])
        retrieve_response = self.client.get(
            retrieve_url,
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(retrieve_response.status_code, 200)
        retrieve_content = json.loads(retrieve_response.content)
        self.assertEqual(retrieve_content['first_name'], 'Integration')
        self.assertEqual(retrieve_content['last_name'], 'Test')
        self.assertEqual(retrieve_content['citizen_id'], citizen_id)
        
        # Step 4: Generate ID card
        id_card_url = reverse('citizen-generate-id-card', args=[db_id])
        id_card_response = self.client.get(
            id_card_url,
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(id_card_response.status_code, 200)
        self.assertEqual(id_card_response['Content-Type'], 'application/pdf')
        
        # Step 5: Verify citizen ID
        verify_url = reverse('citizen-verify-id')
        verify_data = {
            'citizen_id': citizen_id
        }
        
        verify_response = self.client.post(
            verify_url,
            json.dumps(verify_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(verify_response.status_code, 200)
        verify_content = json.loads(verify_response.content)
        self.assertTrue(verify_content['is_valid'])
        self.assertEqual(verify_content['citizen']['first_name'], 'Integration')
        
        # Step 6: Run data aggregation
        aggregate_url = reverse('reports-run-aggregation')
        aggregate_data = {
            'state_id': 1,
            'lga_id': 1
        }
        
        # Add permission to user
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from reporting.models import DemographicStats
        
        content_type = ContentType.objects.get_for_model(DemographicStats)
        permission = Permission.objects.create(
            codename='generate_reports',
            name='Can generate reports',
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        self.user.save()
        
        aggregate_response = self.client.post(
            aggregate_url,
            json.dumps(aggregate_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(aggregate_response.status_code, 200)
        
        # Step 7: Generate demographic report
        report_url = reverse('reports-demographic')
        report_params = {
            'state_id': 1,
            'lga_id': 1
        }
        
        report_response = self.client.get(
            report_url,
            report_params,
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(report_response.status_code, 200)
        report_content = json.loads(report_response.content)
        self.assertEqual(report_content['title'], 'Demographic Report')
        
        # Step 8: Logout
        logout_url = reverse('auth-logout')
        logout_response = self.client.post(
            logout_url,
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        self.assertEqual(logout_response.status_code, 200)
        logout_content = json.loads(logout_response.content)
        self.assertEqual(logout_content['message'], 'Successfully logged out')


class PerformanceTestCase(TestCase):
    """
    Performance tests for the citizen registration system
    """
    
    def setUp(self):
        """
        Set up test data and client
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test client
        self.client = Client()
        
        # Login
        login_url = reverse('auth-login')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        login_response = self.client.post(
            login_url, 
            json.dumps(login_data), 
            content_type='application/json'
        )
        
        login_content = json.loads(login_response.content)
        self.token = login_content['token']
        
        # Create test citizens
        from citizen.models import Citizen
        import random
        
        for i in range(100):
            Citizen.objects.create(
                first_name=f'Test{i}',
                last_name=f'User{i}',
                gender=random.choice(['Male', 'Female']),
                date_of_birth=f'{random.randint(1950, 2000)}-{random.randint(1, 12)}-{random.randint(1, 28)}',
                phone_number=f'080{random.randint(10000000, 99999999)}',
                email=f'test{i}@example.com',
                address=f'{i} Test St',
                residence_state_id=random.randint(1, 3),
                residence_lga_id=random.randint(1, 5),
                residence_ward_id=random.randint(1, 10),
                citizen_id=f'NG-LA-IK-25-{i:06d}-{random.randint(0, 9)}'
            )
    
    def test_search_performance(self):
        """
        Test search performance with large dataset
        """
        import time
        
        # Measure search performance
        search_url = reverse('citizen-search')
        
        start_time = time.time()
        search_response = self.client.get(
            search_url,
            {'query': 'Test'},
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        end_time = time.time()
        
        self.assertEqual(search_response.status_code, 200)
        search_content = json.loads(search_response.content)
        
        # Search should return results
        self.assertGreater(len(search_content['results']), 0)
        
        # Search should be fast (less than 1 second)
        search_time = end_time - start_time
        self.assertLess(search_time, 1.0)
    
    def test_report_generation_performance(self):
        """
        Test report generation performance with large dataset
        """
        import time
        
        # Add permission to user
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from reporting.models import DemographicStats
        
        content_type = ContentType.objects.get_for_model(DemographicStats)
        permission = Permission.objects.create(
            codename='generate_reports',
            name='Can generate reports',
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        self.user.save()
        
        # Run aggregation first
        aggregate_url = reverse('reports-run-aggregation')
        aggregate_data = {}
        
        aggregate_response = self.client.post(
            aggregate_url,
            json.dumps(aggregate_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        
        self.assertEqual(aggregate_response.status_code, 200)
        
        # Measure report generation performance
        report_url = reverse('reports-demographic')
        
        start_time = time.time()
        report_response = self.client.get(
            report_url,
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        end_time = time.time()
        
        self.assertEqual(report_response.status_code, 200)
        
        # Report generation should be reasonably fast (less than 3 seconds)
        report_time = end_time - start_time
        self.assertLess(report_time, 3.0)


if __name__ == '__main__':
    unittest.main()
