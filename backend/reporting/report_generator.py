from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from .models import (
    DemographicStats, OccupationStats, HealthcareStats, 
    FamilyStats, InterestStats, ReportMetadata, CustomReport
)
from django.db import models

class ReportGenerator:
    """
    Service for generating reports and visualizations
    """
    
    def __init__(self):
        self.today = timezone.now().date()
    
    def generate_demographic_report(self, state_id=None, lga_id=None, report_date=None):
        """
        Generate demographic report
        """
        # Use today's date if not specified
        report_date = report_date or self.today
        
        # Build filter conditions
        filters = {'stat_date': report_date}
        if state_id:
            filters['state_id'] = state_id
        if lga_id:
            filters['lga_id'] = lga_id
        
        # Get demographic stats
        stats = DemographicStats.objects.filter(**filters)
        
        # Check if data exists
        if not stats.exists():
            return {
                'success': False,
                'message': 'No demographic data available for the specified parameters'
            }
        
        # Prepare report data
        report_data = {
            'title': 'Demographic Report',
            'generated_at': timezone.now(),
            'parameters': {
                'state_id': state_id,
                'lga_id': lga_id,
                'report_date': report_date
            },
            'sections': []
        }
        
        # Gender distribution
        gender_stats = stats.filter(gender__isnull=False).values('gender').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if gender_stats:
            # Create pie chart for gender distribution
            plt.figure(figsize=(8, 6))
            plt.pie(
                [stat['total'] for stat in gender_stats],
                labels=[stat['gender'] for stat in gender_stats],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Gender Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Gender Distribution',
                'data': list(gender_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Age group distribution
        age_stats = stats.filter(age_group__isnull=False).values('age_group').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('age_group')
        
        if age_stats:
            # Create bar chart for age distribution
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['age_group'] for stat in age_stats],
                y=[stat['total'] for stat in age_stats]
            )
            plt.title('Age Group Distribution')
            plt.xlabel('Age Group')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Age Group Distribution',
                'data': list(age_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Education level distribution
        education_stats = stats.filter(education_level__isnull=False).values('education_level').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if education_stats:
            # Create bar chart for education distribution
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['education_level'] for stat in education_stats],
                y=[stat['total'] for stat in education_stats]
            )
            plt.title('Education Level Distribution')
            plt.xlabel('Education Level')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Education Level Distribution',
                'data': list(education_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Religion distribution
        religion_stats = stats.filter(religion__isnull=False).values('religion').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if religion_stats:
            # Create pie chart for religion distribution
            plt.figure(figsize=(8, 6))
            plt.pie(
                [stat['total'] for stat in religion_stats],
                labels=[stat['religion'] for stat in religion_stats],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Religion Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Religion Distribution',
                'data': list(religion_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Ethnicity distribution
        ethnicity_stats = stats.filter(ethnicity__isnull=False).values('ethnicity').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')[:10]  # Top 10 ethnicities
        
        if ethnicity_stats:
            # Create bar chart for ethnicity distribution
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['ethnicity'] for stat in ethnicity_stats],
                y=[stat['total'] for stat in ethnicity_stats]
            )
            plt.title('Top 10 Ethnicities')
            plt.xlabel('Ethnicity')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Ethnicity Distribution',
                'data': list(ethnicity_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        return {
            'success': True,
            'report': report_data
        }
    
    def generate_occupation_report(self, state_id=None, lga_id=None, report_date=None):
        """
        Generate occupation/career report
        """
        # Use today's date if not specified
        report_date = report_date or self.today
        
        # Build filter conditions
        filters = {'stat_date': report_date}
        if state_id:
            filters['state_id'] = state_id
        if lga_id:
            filters['lga_id'] = lga_id
        
        # Get occupation stats
        stats = OccupationStats.objects.filter(**filters)
        
        # Check if data exists
        if not stats.exists():
            return {
                'success': False,
                'message': 'No occupation data available for the specified parameters'
            }
        
        # Prepare report data
        report_data = {
            'title': 'Occupation and Career Report',
            'generated_at': timezone.now(),
            'parameters': {
                'state_id': state_id,
                'lga_id': lga_id,
                'report_date': report_date
            },
            'sections': []
        }
        
        # Employment status distribution
        employment_stats = stats.filter(employment_status__isnull=False).values('employment_status').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if employment_stats:
            # Create pie chart for employment status
            plt.figure(figsize=(8, 6))
            plt.pie(
                [stat['total'] for stat in employment_stats],
                labels=[stat['employment_status'] for stat in employment_stats],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Employment Status Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Employment Status Distribution',
                'data': list(employment_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Occupation sector distribution
        sector_stats = stats.filter(occupation_sector__isnull=False).values('occupation_sector').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')[:10]  # Top 10 sectors
        
        if sector_stats:
            # Create bar chart for sector distribution
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['occupation_sector'] for stat in sector_stats],
                y=[stat['total'] for stat in sector_stats]
            )
            plt.title('Top 10 Occupation Sectors')
            plt.xlabel('Sector')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Occupation Sector Distribution',
                'data': list(sector_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Income level distribution
        income_stats = stats.filter(income_level__isnull=False).values('income_level').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('income_level')
        
        if income_stats:
            # Create bar chart for income distribution
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['income_level'] for stat in income_stats],
                y=[stat['total'] for stat in income_stats]
            )
            plt.title('Income Level Distribution')
            plt.xlabel('Income Level')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Income Level Distribution',
                'data': list(income_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Qualification level distribution
        qualification_stats = stats.filter(qualification_level__isnull=False).values('qualification_level').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if qualification_stats:
            # Create bar chart for qualification distribution
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['qualification_level'] for stat in qualification_stats],
                y=[stat['total'] for stat in qualification_stats]
            )
            plt.title('Qualification Level Distribution')
            plt.xlabel('Qualification Level')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Qualification Level Distribution',
                'data': list(qualification_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        return {
            'success': True,
            'report': report_data
        }
    
    def generate_healthcare_report(self, state_id=None, lga_id=None, report_date=None):
        """
        Generate healthcare report
        """
        # Use today's date if not specified
        report_date = report_date or self.today
        
        # Build filter conditions
        filters = {'stat_date': report_date}
        if state_id:
            filters['state_id'] = state_id
        if lga_id:
            filters['lga_id'] = lga_id
        
        # Get healthcare stats
        stats = HealthcareStats.objects.filter(**filters)
        
        # Check if data exists
        if not stats.exists():
            return {
                'success': False,
                'message': 'No healthcare data available for the specified parameters'
            }
        
        # Prepare report data
        report_data = {
            'title': 'Healthcare Report',
            'generated_at': timezone.now(),
            'parameters': {
                'state_id': state_id,
                'lga_id': lga_id,
                'report_date': report_date
            },
            'sections': []
        }
        
        # Health condition distribution
        condition_stats = stats.filter(health_condition__isnull=False).values('health_condition').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')[:10]  # Top 10 conditions
        
        if condition_stats:
            # Create bar chart for health conditions
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['health_condition'] for stat in condition_stats],
                y=[stat['total'] for stat in condition_stats]
            )
            plt.title('Top 10 Health Conditions')
            plt.xlabel('Health Condition')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Health Condition Distribution',
                'data': list(condition_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Blood group distribution
        blood_stats = stats.filter(blood_group__isnull=False).values('blood_group').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if blood_stats:
            # Create pie chart for blood groups
            plt.figure(figsize=(8, 6))
            plt.pie(
                [stat['total'] for stat in blood_stats],
                labels=[stat['blood_group'] for stat in blood_stats],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Blood Group Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Blood Group Distribution',
                'data': list(blood_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Disability distribution
        disability_stats = stats.filter(disability_type__isnull=False).values('disability_type').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if disability_stats:
            # Create bar chart for disabilities
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['disability_type'] for stat in disability_stats],
                y=[stat['total'] for stat in disability_stats]
            )
            plt.title('Disability Type Distribution')
            plt.xlabel('Disability Type')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Disability Type Distribution',
                'data': list(disability_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Immunization status distribution
        immunization_stats = stats.filter(immunization_status__isnull=False).values('immunization_status').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if immunization_stats:
            # Create pie chart for immunization status
            plt.figure(figsize=(8, 6))
            plt.pie(
                [stat['total'] for stat in immunization_stats],
                labels=[stat['immunization_status'] for stat in immunization_stats],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Immunization Status Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Immunization Status Distribution',
                'data': list(immunization_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        return {
            'success': True,
            'report': report_data
        }
    
    def generate_family_report(self, state_id=None, lga_id=None, report_date=None):
        """
        Generate family structure report
        """
        # Use today's date if not specified
        report_date = report_date or self.today
        
        # Build filter conditions
        filters = {'stat_date': report_date}
        if state_id:
            filters['state_id'] = state_id
        if lga_id:
            filters['lga_id'] = lga_id
        
        # Get family stats
        stats = FamilyStats.objects.filter(**filters)
        
        # Check if data exists
        if not stats.exists():
            return {
                'success': False,
                'message': 'No family structure data available for the specified parameters'
            }
        
        # Prepare report data
        report_data = {
            'title': 'Family Structure Report',
            'generated_at': timezone.now(),
            'parameters': {
                'state_id': state_id,
                'lga_id': lga_id,
                'report_date': report_date
            },
            'sections': []
        }
        
        # Household size distribution
        household_stats = stats.filter(household_size__isnull=False).values('household_size').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('household_size')
        
        if household_stats:
            # Create bar chart for household size
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['household_size'] for stat in household_stats],
                y=[stat['total'] for stat in household_stats]
            )
            plt.title('Household Size Distribution')
            plt.xlabel('Household Size')
            plt.ylabel('Count')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Household Size Distribution',
                'data': list(household_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Marital status distribution
        marital_stats = stats.filter(marital_status__isnull=False).values('marital_status').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if marital_stats:
            # Create pie chart for marital status
            plt.figure(figsize=(8, 6))
            plt.pie(
                [stat['total'] for stat in marital_stats],
                labels=[stat['marital_status'] for stat in marital_stats],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Marital Status Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Marital Status Distribution',
                'data': list(marital_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Children count distribution
        children_stats = stats.filter(children_count__isnull=False).values('children_count').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('children_count')
        
        if children_stats:
            # Create bar chart for children count
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['children_count'] for stat in children_stats],
                y=[stat['total'] for stat in children_stats]
            )
            plt.title('Number of Children Distribution')
            plt.xlabel('Number of Children')
            plt.ylabel('Count')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Number of Children Distribution',
                'data': list(children_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Family type distribution
        family_type_stats = stats.filter(family_type__isnull=False).values('family_type').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if family_type_stats:
            # Create pie chart for family type
            plt.figure(figsize=(8, 6))
            plt.pie(
                [stat['total'] for stat in family_type_stats],
                labels=[stat['family_type'] for stat in family_type_stats],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Family Type Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Family Type Distribution',
                'data': list(family_type_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        return {
            'success': True,
            'report': report_data
        }
    
    def generate_interests_report(self, state_id=None, lga_id=None, report_date=None):
        """
        Generate interests and sports report
        """
        # Use today's date if not specified
        report_date = report_date or self.today
        
        # Build filter conditions
        filters = {'stat_date': report_date}
        if state_id:
            filters['state_id'] = state_id
        if lga_id:
            filters['lga_id'] = lga_id
        
        # Get interest stats
        stats = InterestStats.objects.filter(**filters)
        
        # Check if data exists
        if not stats.exists():
            return {
                'success': False,
                'message': 'No interests data available for the specified parameters'
            }
        
        # Prepare report data
        report_data = {
            'title': 'Interests and Sports Report',
            'generated_at': timezone.now(),
            'parameters': {
                'state_id': state_id,
                'lga_id': lga_id,
                'report_date': report_date
            },
            'sections': []
        }
        
        # Interest type distribution
        interest_type_stats = stats.filter(interest_type__isnull=False).values('interest_type').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')
        
        if interest_type_stats:
            # Create pie chart for interest types
            plt.figure(figsize=(8, 6))
            plt.pie(
                [stat['total'] for stat in interest_type_stats],
                labels=[stat['interest_type'] for stat in interest_type_stats],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Interest Type Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Interest Type Distribution',
                'data': list(interest_type_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Sports distribution
        sport_stats = stats.filter(sport_name__isnull=False).values('sport_name').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')[:10]  # Top 10 sports
        
        if sport_stats:
            # Create bar chart for sports
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['sport_name'] for stat in sport_stats],
                y=[stat['total'] for stat in sport_stats]
            )
            plt.title('Top 10 Sports')
            plt.xlabel('Sport')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Sports Distribution',
                'data': list(sport_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Cultural activities distribution
        cultural_stats = stats.filter(cultural_activity__isnull=False).values('cultural_activity').annotate(
            total=models.Sum('count'),
            avg_percentage=models.Avg('percentage')
        ).order_by('-total')[:10]  # Top 10 cultural activities
        
        if cultural_stats:
            # Create bar chart for cultural activities
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[stat['cultural_activity'] for stat in cultural_stats],
                y=[stat['total'] for stat in cultural_stats]
            )
            plt.title('Top 10 Cultural Activities')
            plt.xlabel('Cultural Activity')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add section to report
            report_data['sections'].append({
                'title': 'Cultural Activities Distribution',
                'data': list(cultural_stats),
                'chart': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        return {
            'success': True,
            'report': report_data
        }
    
    def generate_executive_dashboard(self, state_id=None, report_date=None):
        """
        Generate executive dashboard with key metrics
        """
        # Use today's date if not specified
        report_date = report_date or self.today
        
        # Build filter conditions
        filters = {'stat_date': report_date}
        if state_id:
            filters['state_id'] = state_id
        
        # Prepare dashboard data
        dashboard_data = {
            'title': 'Executive Dashboard',
            'generated_at': timezone.now(),
            'parameters': {
                'state_id': state_id,
                'report_date': report_date
            },
            'metrics': [],
            'charts': []
        }
        
        # Total population
        total_population = DemographicStats.objects.filter(
            gender__isnull=False, **filters
        ).aggregate(total=models.Sum('count'))['total'] or 0
        
        dashboard_data['metrics'].append({
            'name': 'Total Population',
            'value': total_population,
            'icon': 'users'
        })
        
        # Employment rate
        employed_count = OccupationStats.objects.filter(
            employment_status='Employed', **filters
        ).aggregate(total=models.Sum('count'))['total'] or 0
        
        unemployed_count = OccupationStats.objects.filter(
            employment_status='Unemployed', **filters
        ).aggregate(total=models.Sum('count'))['total'] or 0
        
        if employed_count + unemployed_count > 0:
            employment_rate = (employed_count / (employed_count + unemployed_count)) * 100
        else:
            employment_rate = 0
        
        dashboard_data['metrics'].append({
            'name': 'Employment Rate',
            'value': f"{employment_rate:.1f}%",
            'icon': 'briefcase'
        })
        
        # Average household size
        avg_household_size = FamilyStats.objects.filter(
            household_size__isnull=False, **filters
        ).aggregate(
            avg=models.Avg('household_size')
        )['avg'] or 0
        
        dashboard_data['metrics'].append({
            'name': 'Avg. Household Size',
            'value': f"{avg_household_size:.1f}",
            'icon': 'home'
        })
        
        # Health conditions chart
        health_conditions = HealthcareStats.objects.filter(
            health_condition__isnull=False, **filters
        ).values('health_condition').annotate(
            total=models.Sum('count')
        ).order_by('-total')[:5]  # Top 5 health conditions
        
        if health_conditions:
            # Create bar chart for health conditions
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[condition['health_condition'] for condition in health_conditions],
                y=[condition['total'] for condition in health_conditions]
            )
            plt.title('Top 5 Health Conditions')
            plt.xlabel('Health Condition')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add chart to dashboard
            dashboard_data['charts'].append({
                'title': 'Top 5 Health Conditions',
                'type': 'bar',
                'image': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Age distribution chart
        age_distribution = DemographicStats.objects.filter(
            age_group__isnull=False, **filters
        ).values('age_group').annotate(
            total=models.Sum('count')
        ).order_by('age_group')
        
        if age_distribution:
            # Create pie chart for age distribution
            plt.figure(figsize=(8, 6))
            plt.pie(
                [age['total'] for age in age_distribution],
                labels=[age['age_group'] for age in age_distribution],
                autopct='%1.1f%%',
                startangle=90
            )
            plt.axis('equal')
            plt.title('Age Distribution')
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add chart to dashboard
            dashboard_data['charts'].append({
                'title': 'Age Distribution',
                'type': 'pie',
                'image': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        # Education level chart
        education_levels = DemographicStats.objects.filter(
            education_level__isnull=False, **filters
        ).values('education_level').annotate(
            total=models.Sum('count')
        ).order_by('-total')
        
        if education_levels:
            # Create bar chart for education levels
            plt.figure(figsize=(10, 6))
            sns.barplot(
                x=[level['education_level'] for level in education_levels],
                y=[level['total'] for level in education_levels]
            )
            plt.title('Education Level Distribution')
            plt.xlabel('Education Level')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Save chart to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            buffer.seek(0)
            
            # Add chart to dashboard
            dashboard_data['charts'].append({
                'title': 'Education Level Distribution',
                'type': 'bar',
                'image': base64.b64encode(buffer.getvalue()).decode('utf-8')
            })
        
        return {
            'success': True,
            'dashboard': dashboard_data
        }
    
    def execute_custom_report(self, report_id, parameters=None):
        """
        Execute a custom report
        """
        try:
            # Get custom report definition
            custom_report = CustomReport.objects.get(pk=report_id)
            
            # Replace parameters in query
            query = custom_report.report_query
            if parameters:
                for key, value in parameters.items():
                    query = query.replace(f":{key}", f"'{value}'")
            
            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return {
                'success': True,
                'report': {
                    'title': custom_report.report_name,
                    'description': custom_report.report_description,
                    'generated_at': timezone.now(),
                    'parameters': parameters,
                    'columns': columns,
                    'data': results
                }
            }
        except CustomReport.DoesNotExist:
            return {
                'success': False,
                'message': f'Custom report with ID {report_id} not found'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error executing custom report: {str(e)}'
            }
