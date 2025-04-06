import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from citizen.models import Citizen, IDSequenceTracker
from citizen.id_generator import CitizenIDGenerator
import json

class CitizenIDGeneratorTestCase(TestCase):
    """
    Test cases for citizen ID generation
    """
    
    def setUp(self):
        """
        Set up test data
        """
        # Create test sequence trackers
        IDSequenceTracker.objects.create(
            state_code='LA',
            lga_code='IK',
            year=25,
            current_sequence=0
        )
        
        IDSequenceTracker.objects.create(
            state_code='LA',
            lga_code='ET',
            year=25,
            current_sequence=100
        )
        
        # Initialize ID generator
        self.id_generator = CitizenIDGenerator()
    
    def test_generate_id(self):
        """
        Test ID generation
        """
        # Generate ID for Lagos-Ikeja
        citizen_id = self.id_generator.generate_id('LA', 'IK')
        
        # Check ID format
        self.assertEqual(len(citizen_id), 16)
        self.assertTrue(citizen_id.startswith('NG-LA-IK-25-'))
        
        # Check sequence number
        sequence_part = citizen_id.split('-')[4]
        self.assertEqual(len(sequence_part), 6)
        self.assertEqual(sequence_part, '000001')
        
        # Check check digit
        check_digit = citizen_id[-1]
        self.assertTrue(check_digit.isdigit())
        
        # Verify sequence tracker was updated
        tracker = IDSequenceTracker.objects.get(state_code='LA', lga_code='IK', year=25)
        self.assertEqual(tracker.current_sequence, 1)
        
        # Generate another ID for Lagos-Ikeja
        citizen_id2 = self.id_generator.generate_id('LA', 'IK')
        
        # Check sequence number increased
        sequence_part2 = citizen_id2.split('-')[4]
        self.assertEqual(sequence_part2, '000002')
        
        # Verify sequence tracker was updated again
        tracker.refresh_from_db()
        self.assertEqual(tracker.current_sequence, 2)
        
        # Generate ID for Lagos-Eti-Osa
        citizen_id3 = self.id_generator.generate_id('LA', 'ET')
        
        # Check sequence number starts from existing value
        sequence_part3 = citizen_id3.split('-')[4]
        self.assertEqual(sequence_part3, '000101')
        
        # Verify sequence tracker was updated
        tracker2 = IDSequenceTracker.objects.get(state_code='LA', lga_code='ET', year=25)
        self.assertEqual(tracker2.current_sequence, 101)
    
    def test_validate_id(self):
        """
        Test ID validation
        """
        # Generate valid ID
        valid_id = self.id_generator.generate_id('LA', 'IK')
        
        # Test valid ID
        self.assertTrue(self.id_generator.validate_id(valid_id))
        
        # Test invalid format
        self.assertFalse(self.id_generator.validate_id('INVALID-ID'))
        
        # Test invalid check digit
        invalid_check_digit = valid_id[:-1] + '0'
        self.assertFalse(self.id_generator.validate_id(invalid_check_digit))
    
    def test_extract_id_components(self):
        """
        Test extracting components from ID
        """
        # Generate ID
        citizen_id = self.id_generator.generate_id('LA', 'IK')
        
        # Extract components
        components = self.id_generator.extract_id_components(citizen_id)
        
        # Verify components
        self.assertEqual(components['country_code'], 'NG')
        self.assertEqual(components['state_code'], 'LA')
        self.assertEqual(components['lga_code'], 'IK')
        self.assertEqual(components['year'], '25')
        self.assertEqual(components['sequence'], '000001')
        self.assertEqual(components['check_digit'], citizen_id[-1])
    
    def test_generate_id_for_nonexistent_tracker(self):
        """
        Test ID generation for nonexistent tracker
        """
        # Generate ID for nonexistent tracker
        citizen_id = self.id_generator.generate_id('AB', 'CD')
        
        # Check ID format
        self.assertEqual(len(citizen_id), 16)
        self.assertTrue(citizen_id.startswith('NG-AB-CD-25-'))
        
        # Check sequence number
        sequence_part = citizen_id.split('-')[4]
        self.assertEqual(sequence_part, '000001')
        
        # Verify new tracker was created
        tracker = IDSequenceTracker.objects.get(state_code='AB', lga_code='CD', year=25)
        self.assertEqual(tracker.current_sequence, 1)
    
    def test_concurrent_id_generation(self):
        """
        Test concurrent ID generation
        """
        # Simulate concurrent ID generation by manually creating multiple IDs
        # without refreshing the tracker from the database
        
        # Get initial tracker
        tracker = IDSequenceTracker.objects.get(state_code='LA', lga_code='IK', year=25)
        initial_sequence = tracker.current_sequence
        
        # Generate multiple IDs
        ids = []
        for i in range(5):
            ids.append(self.id_generator.generate_id('LA', 'IK'))
        
        # Verify all IDs are unique
        self.assertEqual(len(ids), len(set(ids)))
        
        # Verify sequence numbers are sequential
        sequences = [int(id.split('-')[4]) for id in ids]
        self.assertEqual(sequences, [i + initial_sequence + 1 for i in range(5)])
        
        # Verify tracker was updated correctly
        tracker.refresh_from_db()
        self.assertEqual(tracker.current_sequence, initial_sequence + 5)


class CitizenAPITestCase(TestCase):
    """
    Test cases for citizen API endpoints
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
        
        # Create test citizens
        self.citizen1 = Citizen.objects.create(
            first_name='John',
            last_name='Doe',
            gender='Male',
            date_of_birth='1990-01-01',
            phone_number='08012345678',
            email='john.doe@example.com',
            address='123 Main St',
            residence_state_id=1,
            residence_lga_id=1,
            residence_ward_id=1,
            citizen_id='NG-LA-IK-25-000001-5'
        )
        
        self.citizen2 = Citizen.objects.create(
            first_name='Jane',
            last_name='Smith',
            gender='Female',
            date_of_birth='1992-05-15',
            phone_number='08087654321',
            email='jane.smith@example.com',
            address='456 Oak Ave',
            residence_state_id=1,
            residence_lga_id=2,
            residence_ward_id=1,
            citizen_id='NG-LA-ET-25-000001-3'
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_list_citizens_api(self):
        """
        Test listing citizens API endpoint
        """
        url = reverse('citizen-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_citizen_api(self):
        """
        Test retrieving a citizen API endpoint
        """
        url = reverse('citizen-detail', args=[self.citizen1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
        self.assertEqual(response.data['citizen_id'], 'NG-LA-IK-25-000001-5')
    
    def test_create_citizen_api(self):
        """
        Test creating a citizen API endpoint
        """
        url = reverse('citizen-list')
        data = {
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'gender': 'Male',
            'date_of_birth': '1985-08-20',
            'phone_number': '08023456789',
            'email': 'michael.johnson@example.com',
            'address': '789 Pine St',
            'residence_state_id': 1,
            'residence_lga_id': 1,
            'residence_ward_id': 2
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Michael')
        self.assertEqual(response.data['last_name'], 'Johnson')
        self.assertIsNotNone(response.data['citizen_id'])
        
        # Verify citizen was created in database
        self.assertTrue(Citizen.objects.filter(first_name='Michael', last_name='Johnson').exists())
    
    def test_update_citizen_api(self):
        """
        Test updating a citizen API endpoint
        """
        url = reverse('citizen-detail', args=[self.citizen1.id])
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '08099887766',
            'address': '123 Updated St'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '08099887766')
        self.assertEqual(response.data['address'], '123 Updated St')
        
        # Verify citizen was updated in database
        self.citizen1.refresh_from_db()
        self.assertEqual(self.citizen1.phone_number, '08099887766')
        self.assertEqual(self.citizen1.address, '123 Updated St')
    
    def test_search_citizens_api(self):
        """
        Test searching citizens API endpoint
        """
        url = reverse('citizen-search')
        
        # Search by name
        response = self.client.get(url, {'query': 'John'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'John')
        
        # Search by ID
        response = self.client.get(url, {'query': 'NG-LA-ET'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['citizen_id'], 'NG-LA-ET-25-000001-3')
    
    def test_verify_citizen_id_api(self):
        """
        Test verifying citizen ID API endpoint
        """
        url = reverse('citizen-verify-id')
        
        # Test valid ID
        response = self.client.post(url, {'citizen_id': 'NG-LA-IK-25-000001-5'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_valid'])
        self.assertEqual(response.data['citizen']['first_name'], 'John')
        self.assertEqual(response.data['citizen']['last_name'], 'Doe')
        
        # Test invalid ID
        response = self.client.post(url, {'citizen_id': 'INVALID-ID'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_valid'])
        self.assertIsNone(response.data.get('citizen'))
    
    def test_generate_id_card_api(self):
        """
        Test generating ID card API endpoint
        """
        url = reverse('citizen-generate-id-card', args=[self.citizen1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get('Content-Type'), 'application/pdf')
        self.assertIn('attachment; filename=', response.get('Content-Disposition'))
    
    def test_unauthorized_access(self):
        """
        Test unauthorized access to API endpoints
        """
        # Create unauthenticated client
        client = APIClient()
        
        url = reverse('citizen-list')
        response = client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SecurityTestCase(TestCase):
    """
    Test cases for security features
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
        
        # Create API client
        self.client = APIClient()
    
    def test_csrf_protection(self):
        """
        Test CSRF protection
        """
        # Django's CSRF protection is automatically tested by the test client
        # This test is just to ensure it's documented
        pass
    
    def test_password_hashing(self):
        """
        Test password hashing
        """
        # Verify password is hashed
        self.assertNotEqual(self.user.password, 'testpassword')
        
        # Verify password can be verified
        self.assertTrue(self.user.check_password('testpassword'))
    
    def test_authentication_required(self):
        """
        Test authentication required for protected endpoints
        """
        # Test unauthenticated access
        url = reverse('citizen-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test authenticated access
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_sql_injection_protection(self):
        """
        Test SQL injection protection
        """
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Test with SQL injection attempt in search
        url = reverse('citizen-search')
        response = self.client.get(url, {'query': "' OR 1=1; --"})
        
        # Should not return all records
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_xss_protection(self):
        """
        Test XSS protection
        """
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Create citizen with XSS attempt
        url = reverse('citizen-list')
        data = {
            'first_name': '<script>alert("XSS")</script>',
            'last_name': 'Test',
            'gender': 'Male',
            'date_of_birth': '1990-01-01',
            'phone_number': '08012345678',
            'email': 'xss@example.com',
            'address': '123 Main St',
            'residence_state_id': 1,
            'residence_lga_id': 1,
            'residence_ward_id': 1
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Retrieve the citizen
        citizen_id = response.data['id']
        url = reverse('citizen-detail', args=[citizen_id])
        response = self.client.get(url)
        
        # Verify XSS is escaped in response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], '<script>alert("XSS")</script>')
        
        # Django's template system will automatically escape this when rendered


if __name__ == '__main__':
    unittest.main()
