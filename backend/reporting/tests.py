import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from reporting.models import (
    DemographicStats, OccupationStats, HealthcareStats, 
    FamilyStats, InterestStats, ReportMetadata, CustomReport
)
from reporting.data_aggregator import DataAggregator
from reporting.report_generator import ReportGenerator
from django.utils import timezone
from datetime import date, timedelta
import json

class ReportingModelsTestCase(TestCase):
    """
    Test cases for reporting models
    """
    
    def setUp(self):
        """
        Set up test data
        """
        # Create test state, LGA, and ward
        self.state_id = 1
        self.lga_id = 1
        self.ward_id = 1
        
        # Create test date
        self.test_date = timezone.now().date()
        
        # Create test demographic stats
        DemographicStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            gender='Male',
            count=100,
            percentage=60.0
        )
        
        DemographicStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            gender='Female',
            count=67,
            percentage=40.0
        )
        
        # Create test occupation stats
        OccupationStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            employment_status='Employed',
            count=120,
            percentage=72.0
        )
        
        OccupationStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            employment_status='Unemployed',
            count=47,
            percentage=28.0
        )
        
        # Create test healthcare stats
        HealthcareStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            blood_group='O+',
            count=70,
            percentage=42.0
        )
        
        # Create test family stats
        FamilyStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            household_size='3-4',
            count=85,
            percentage=51.0
        )
        
        # Create test interest stats
        InterestStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            interest_type='Sport',
            sport_name='Football',
            count=45,
            percentage=27.0
        )
        
        # Create test report metadata
        ReportMetadata.objects.create(
            report_name='demographic_aggregation',
            last_generated=timezone.now(),
            generation_duration=10,
            is_cached=True,
            cache_expiry=timezone.now() + timedelta(days=1)
        )
        
        # Create test user for custom reports
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test custom report
        CustomReport.objects.create(
            user=self.user,
            report_name='Test Custom Report',
            report_description='A test custom report',
            report_query='SELECT * FROM demographic_stats WHERE state_id = :state_id',
            parameters={'state_id': 1}
        )
    
    def test_demographic_stats_model(self):
        """
        Test demographic stats model
        """
        stats = DemographicStats.objects.filter(gender='Male').first()
        self.assertEqual(stats.count, 100)
        self.assertEqual(stats.percentage, 60.0)
        self.assertEqual(stats.state_id, self.state_id)
        self.assertEqual(stats.lga_id, self.lga_id)
        self.assertEqual(stats.ward_id, self.ward_id)
        self.assertEqual(stats.stat_date, self.test_date)
    
    def test_occupation_stats_model(self):
        """
        Test occupation stats model
        """
        stats = OccupationStats.objects.filter(employment_status='Employed').first()
        self.assertEqual(stats.count, 120)
        self.assertEqual(stats.percentage, 72.0)
        self.assertEqual(stats.state_id, self.state_id)
        self.assertEqual(stats.lga_id, self.lga_id)
        self.assertEqual(stats.ward_id, self.ward_id)
        self.assertEqual(stats.stat_date, self.test_date)
    
    def test_healthcare_stats_model(self):
        """
        Test healthcare stats model
        """
        stats = HealthcareStats.objects.filter(blood_group='O+').first()
        self.assertEqual(stats.count, 70)
        self.assertEqual(stats.percentage, 42.0)
        self.assertEqual(stats.state_id, self.state_id)
        self.assertEqual(stats.lga_id, self.lga_id)
        self.assertEqual(stats.ward_id, self.ward_id)
        self.assertEqual(stats.stat_date, self.test_date)
    
    def test_family_stats_model(self):
        """
        Test family stats model
        """
        stats = FamilyStats.objects.filter(household_size='3-4').first()
        self.assertEqual(stats.count, 85)
        self.assertEqual(stats.percentage, 51.0)
        self.assertEqual(stats.state_id, self.state_id)
        self.assertEqual(stats.lga_id, self.lga_id)
        self.assertEqual(stats.ward_id, self.ward_id)
        self.assertEqual(stats.stat_date, self.test_date)
    
    def test_interest_stats_model(self):
        """
        Test interest stats model
        """
        stats = InterestStats.objects.filter(sport_name='Football').first()
        self.assertEqual(stats.count, 45)
        self.assertEqual(stats.percentage, 27.0)
        self.assertEqual(stats.interest_type, 'Sport')
        self.assertEqual(stats.state_id, self.state_id)
        self.assertEqual(stats.lga_id, self.lga_id)
        self.assertEqual(stats.ward_id, self.ward_id)
        self.assertEqual(stats.stat_date, self.test_date)
    
    def test_report_metadata_model(self):
        """
        Test report metadata model
        """
        metadata = ReportMetadata.objects.filter(report_name='demographic_aggregation').first()
        self.assertEqual(metadata.generation_duration, 10)
        self.assertTrue(metadata.is_cached)
        self.assertIsNotNone(metadata.cache_expiry)
    
    def test_custom_report_model(self):
        """
        Test custom report model
        """
        report = CustomReport.objects.filter(report_name='Test Custom Report').first()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.report_description, 'A test custom report')
        self.assertEqual(report.report_query, 'SELECT * FROM demographic_stats WHERE state_id = :state_id')
        self.assertEqual(report.parameters, {'state_id': 1})


class ReportGeneratorTestCase(TestCase):
    """
    Test cases for report generator
    """
    
    def setUp(self):
        """
        Set up test data
        """
        # Create test state, LGA, and ward
        self.state_id = 1
        self.lga_id = 1
        self.ward_id = 1
        
        # Create test date
        self.test_date = timezone.now().date()
        
        # Create test demographic stats
        DemographicStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            gender='Male',
            count=100,
            percentage=60.0
        )
        
        DemographicStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            gender='Female',
            count=67,
            percentage=40.0
        )
        
        # Create test occupation stats
        OccupationStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            employment_status='Employed',
            count=120,
            percentage=72.0
        )
        
        OccupationStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            employment_status='Unemployed',
            count=47,
            percentage=28.0
        )
        
        # Create test user for custom reports
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test custom report
        self.custom_report = CustomReport.objects.create(
            user=self.user,
            report_name='Test Custom Report',
            report_description='A test custom report',
            report_query='SELECT * FROM reporting_demographicstats WHERE state_id = :state_id',
            parameters={'state_id': 1}
        )
        
        # Initialize report generator
        self.report_generator = ReportGenerator()
    
    def test_generate_demographic_report(self):
        """
        Test demographic report generation
        """
        result = self.report_generator.generate_demographic_report(
            state_id=self.state_id,
            lga_id=self.lga_id,
            report_date=self.test_date
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['title'], 'Demographic Report')
        self.assertEqual(result['report']['parameters']['state_id'], self.state_id)
        self.assertEqual(result['report']['parameters']['lga_id'], self.lga_id)
        self.assertEqual(result['report']['parameters']['report_date'], self.test_date)
        
        # Check if gender section exists
        gender_section = None
        for section in result['report']['sections']:
            if section['title'] == 'Gender Distribution':
                gender_section = section
                break
        
        self.assertIsNotNone(gender_section)
        self.assertEqual(len(gender_section['data']), 2)  # Male and Female
        
        # Check data values
        male_data = None
        female_data = None
        for item in gender_section['data']:
            if item['gender'] == 'Male':
                male_data = item
            elif item['gender'] == 'Female':
                female_data = item
        
        self.assertIsNotNone(male_data)
        self.assertIsNotNone(female_data)
        self.assertEqual(male_data['total'], 100)
        self.assertEqual(female_data['total'], 67)
    
    def test_generate_occupation_report(self):
        """
        Test occupation report generation
        """
        result = self.report_generator.generate_occupation_report(
            state_id=self.state_id,
            lga_id=self.lga_id,
            report_date=self.test_date
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['title'], 'Occupation and Career Report')
        self.assertEqual(result['report']['parameters']['state_id'], self.state_id)
        self.assertEqual(result['report']['parameters']['lga_id'], self.lga_id)
        self.assertEqual(result['report']['parameters']['report_date'], self.test_date)
        
        # Check if employment section exists
        employment_section = None
        for section in result['report']['sections']:
            if section['title'] == 'Employment Status Distribution':
                employment_section = section
                break
        
        self.assertIsNotNone(employment_section)
        self.assertEqual(len(employment_section['data']), 2)  # Employed and Unemployed
        
        # Check data values
        employed_data = None
        unemployed_data = None
        for item in employment_section['data']:
            if item['employment_status'] == 'Employed':
                employed_data = item
            elif item['employment_status'] == 'Unemployed':
                unemployed_data = item
        
        self.assertIsNotNone(employed_data)
        self.assertIsNotNone(unemployed_data)
        self.assertEqual(employed_data['total'], 120)
        self.assertEqual(unemployed_data['total'], 47)
    
    def test_generate_executive_dashboard(self):
        """
        Test executive dashboard generation
        """
        result = self.report_generator.generate_executive_dashboard(
            state_id=self.state_id,
            report_date=self.test_date
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['dashboard']['title'], 'Executive Dashboard')
        self.assertEqual(result['dashboard']['parameters']['state_id'], self.state_id)
        self.assertEqual(result['dashboard']['parameters']['report_date'], self.test_date)
        
        # Check metrics
        self.assertGreater(len(result['dashboard']['metrics']), 0)
        
        # Find employment rate metric
        employment_rate_metric = None
        for metric in result['dashboard']['metrics']:
            if metric['name'] == 'Employment Rate':
                employment_rate_metric = metric
                break
        
        self.assertIsNotNone(employment_rate_metric)
        self.assertEqual(employment_rate_metric['value'], '71.9%')
    
    def test_execute_custom_report(self):
        """
        Test custom report execution
        """
        result = self.report_generator.execute_custom_report(
            self.custom_report.pk,
            {'state_id': self.state_id}
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['report']['title'], 'Test Custom Report')
        self.assertEqual(result['report']['description'], 'A test custom report')
        self.assertEqual(result['report']['parameters'], {'state_id': self.state_id})
        self.assertGreater(len(result['report']['data']), 0)
    
    def test_report_with_invalid_parameters(self):
        """
        Test report generation with invalid parameters
        """
        # Test with non-existent state
        result = self.report_generator.generate_demographic_report(
            state_id=999,
            report_date=self.test_date
        )
        
        self.assertFalse(result['success'])
        self.assertIn('No demographic data available', result['message'])
        
        # Test with non-existent date
        result = self.report_generator.generate_demographic_report(
            state_id=self.state_id,
            report_date=date(2000, 1, 1)
        )
        
        self.assertFalse(result['success'])
        self.assertIn('No demographic data available', result['message'])


class ReportAPITestCase(TestCase):
    """
    Test cases for report API endpoints
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
        
        # Create test state, LGA, and ward
        self.state_id = 1
        self.lga_id = 1
        self.ward_id = 1
        
        # Create test date
        self.test_date = timezone.now().date()
        
        # Create test demographic stats
        DemographicStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            gender='Male',
            count=100,
            percentage=60.0
        )
        
        DemographicStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            gender='Female',
            count=67,
            percentage=40.0
        )
        
        # Create test occupation stats
        OccupationStats.objects.create(
            stat_date=self.test_date,
            state_id=self.state_id,
            lga_id=self.lga_id,
            ward_id=self.ward_id,
            employment_status='Employed',
            count=120,
            percentage=72.0
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_demographic_report_api(self):
        """
        Test demographic report API endpoint
        """
        url = reverse('reports-demographic')
        response = self.client.get(url, {
            'state_id': self.state_id,
            'lga_id': self.lga_id,
            'report_date': self.test_date.isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Demographic Report')
        self.assertEqual(response.data['parameters']['state_id'], str(self.state_id))
        self.assertEqual(response.data['parameters']['lga_id'], str(self.lga_id))
        self.assertGreater(len(response.data['sections']), 0)
    
    def test_occupation_report_api(self):
        """
        Test occupation report API endpoint
        """
        url = reverse('reports-occupation')
        response = self.client.get(url, {
            'state_id': self.state_id,
            'lga_id': self.lga_id,
            'report_date': self.test_date.isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Occupation and Career Report')
        self.assertEqual(response.data['parameters']['state_id'], str(self.state_id))
        self.assertEqual(response.data['parameters']['lga_id'], str(self.lga_id))
        self.assertGreater(len(response.data['sections']), 0)
    
    def test_executive_dashboard_api(self):
        """
        Test executive dashboard API endpoint
        """
        url = reverse('reports-executive-dashboard')
        response = self.client.get(url, {
            'state_id': self.state_id,
            'report_date': self.test_date.isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Executive Dashboard')
        self.assertEqual(response.data['parameters']['state_id'], str(self.state_id))
        self.assertGreater(len(response.data['metrics']), 0)
    
    def test_export_csv_api(self):
        """
        Test CSV export API endpoint
        """
        url = reverse('reports-export-csv')
        response = self.client.get(url, {
            'type': 'demographic',
            'state_id': self.state_id,
            'lga_id': self.lga_id,
            'report_date': self.test_date.isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="demographic_report_', response['Content-Disposition'])
    
    def test_run_aggregation_api(self):
        """
        Test run aggregation API endpoint
        """
        # Add permission to user
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(DemographicStats)
        permission = Permission.objects.create(
            codename='generate_reports',
            name='Can generate reports',
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        self.user.save()
        
        url = reverse('reports-run-aggregation')
        response = self.client.post(url, {
            'state_id': self.state_id,
            'lga_id': self.lga_id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Data aggregation completed successfully')
    
    def test_unauthorized_access(self):
        """
        Test unauthorized access to API endpoints
        """
        # Create unauthenticated client
        client = APIClient()
        
        url = reverse('reports-demographic')
        response = client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


if __name__ == '__main__':
    unittest.main()
