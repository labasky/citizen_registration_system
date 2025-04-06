# Reporting and Analytics System Design

## 1. Overview

The Reporting and Analytics System is a critical component of the Citizen Registration System that provides insights and statistics based on citizen data. This system will enable government officials to make data-driven decisions by analyzing demographic information, career distributions, healthcare needs, family structures, and other important metrics. This document outlines the design and implementation of the reporting and analytics features.

## 2. Reporting Requirements

### 2.1 Demographic Reports

- Population distribution by age, gender, and location
- Population density maps by LGA and ward
- Population growth trends over time
- Citizenship status distribution
- Educational level distribution
- Religious and ethnic distribution (where applicable)

### 2.2 Career/Occupation Analytics

- Employment status distribution
- Occupation sector distribution
- Income level distribution
- Professional qualification distribution
- Unemployment rates by location and age group
- Skill availability mapping

### 2.3 Healthcare Statistics

- Health condition prevalence
- Disability distribution
- Healthcare access metrics
- Immunization coverage
- Blood group distribution
- Common health challenges by region

### 2.4 Family Structure Analytics

- Household size distribution
- Marital status distribution
- Number of children distribution
- Extended family relationships
- Orphan and vulnerable children statistics
- Elderly population statistics

### 2.5 Sports/Interests Distribution

- Popular sports by region
- Interest group distribution
- Talent mapping for sports development
- Cultural activity participation

### 2.6 Executive Dashboards

- High-level overview of key metrics
- Comparative analysis between regions
- Trend analysis over time
- Anomaly detection and alerts
- Policy impact assessment

## 3. Data Aggregation and Processing

### 3.1 Data Aggregation Strategy

The system will use a combination of real-time and batch processing approaches:

1. **Real-time Aggregation**: For frequently accessed metrics and dashboard displays
2. **Scheduled Batch Processing**: For complex reports and in-depth analytics
3. **On-demand Processing**: For custom reports requested by users

### 3.2 Data Processing Pipeline

1. **Data Extraction**: Retrieve relevant data from the main database
2. **Data Transformation**: Clean, normalize, and prepare data for analysis
3. **Data Aggregation**: Compute statistics and metrics
4. **Data Storage**: Store processed results in a reporting database
5. **Data Presentation**: Display results through the user interface

### 3.3 Caching Strategy

- Frequently accessed reports will be cached to improve performance
- Cache invalidation will occur when new data is added or existing data is modified
- Time-based cache expiration for reports that change frequently
- Permanent caching for historical reports that don't change

## 4. Implementation Details

### 4.1 Database Schema for Analytics

```sql
-- Reporting database schema

-- Demographic aggregation table
CREATE TABLE demographic_stats (
    stat_id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    state_id INTEGER REFERENCES states(id),
    lga_id INTEGER REFERENCES local_government_areas(id),
    ward_id INTEGER REFERENCES wards(id),
    age_group VARCHAR(20),
    gender VARCHAR(10),
    education_level VARCHAR(50),
    religion VARCHAR(50),
    ethnicity VARCHAR(50),
    count INTEGER NOT NULL,
    percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Career/Occupation aggregation table
CREATE TABLE occupation_stats (
    stat_id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    state_id INTEGER REFERENCES states(id),
    lga_id INTEGER REFERENCES local_government_areas(id),
    ward_id INTEGER REFERENCES wards(id),
    occupation_sector VARCHAR(100),
    employment_status VARCHAR(50),
    income_level VARCHAR(50),
    qualification_level VARCHAR(50),
    count INTEGER NOT NULL,
    percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Healthcare aggregation table
CREATE TABLE healthcare_stats (
    stat_id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    state_id INTEGER REFERENCES states(id),
    lga_id INTEGER REFERENCES local_government_areas(id),
    ward_id INTEGER REFERENCES wards(id),
    health_condition VARCHAR(100),
    disability_type VARCHAR(100),
    blood_group VARCHAR(10),
    immunization_status VARCHAR(50),
    count INTEGER NOT NULL,
    percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Family structure aggregation table
CREATE TABLE family_stats (
    stat_id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    state_id INTEGER REFERENCES states(id),
    lga_id INTEGER REFERENCES local_government_areas(id),
    ward_id INTEGER REFERENCES wards(id),
    household_size INTEGER,
    marital_status VARCHAR(50),
    children_count INTEGER,
    family_type VARCHAR(50),
    count INTEGER NOT NULL,
    percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sports/Interests aggregation table
CREATE TABLE interest_stats (
    stat_id SERIAL PRIMARY KEY,
    stat_date DATE NOT NULL,
    state_id INTEGER REFERENCES states(id),
    lga_id INTEGER REFERENCES local_government_areas(id),
    ward_id INTEGER REFERENCES wards(id),
    interest_type VARCHAR(100),
    sport_name VARCHAR(100),
    cultural_activity VARCHAR(100),
    count INTEGER NOT NULL,
    percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Report metadata table
CREATE TABLE report_metadata (
    report_id SERIAL PRIMARY KEY,
    report_name VARCHAR(100) NOT NULL,
    report_description TEXT,
    last_generated TIMESTAMP,
    generation_duration INTEGER, -- in seconds
    is_cached BOOLEAN DEFAULT FALSE,
    cache_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Custom report definitions
CREATE TABLE custom_reports (
    custom_report_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    report_name VARCHAR(100) NOT NULL,
    report_description TEXT,
    report_query TEXT NOT NULL,
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Data Aggregation Service

```python
# data_aggregator.py
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .models import (
    DemographicStats, OccupationStats, HealthcareStats, 
    FamilyStats, InterestStats, ReportMetadata
)
from citizen.models import Citizen, Education, Occupation, Health, Family, Interest

class DataAggregator:
    """
    Service for aggregating citizen data for reporting and analytics
    """
    
    def __init__(self):
        self.today = timezone.now().date()
    
    def aggregate_all_data(self):
        """
        Run all aggregation processes
        """
        self.aggregate_demographics()
        self.aggregate_occupations()
        self.aggregate_healthcare()
        self.aggregate_family_structures()
        self.aggregate_interests()
        
        # Update report metadata
        self._update_report_metadata("all_aggregations")
    
    def aggregate_demographics(self, state_id=None, lga_id=None):
        """
        Aggregate demographic data
        """
        start_time = timezone.now()
        
        # Build filter conditions
        filters = {}
        if state_id:
            filters['residence_state_id'] = state_id
        if lga_id:
            filters['residence_lga_id'] = lga_id
        
        # Get citizens based on filters
        citizens = Citizen.objects.filter(**filters)
        
        # Use pandas for efficient aggregation
        df = pd.DataFrame(list(citizens.values(
            'residence_state_id', 'residence_lga_id', 'residence_ward_id',
            'gender', 'date_of_birth', 'education__level', 'religion', 'ethnicity'
        )))
        
        # Calculate age from date of birth
        df['age'] = df['date_of_birth'].apply(
            lambda x: (self.today - x).days // 365 if x else None
        )
        
        # Create age groups
        df['age_group'] = pd.cut(
            df['age'],
            bins=[0, 5, 12, 18, 25, 35, 50, 65, 120],
            labels=['0-5', '6-12', '13-18', '19-25', '26-35', '36-50', '51-65', '65+']
        )
        
        # Group by different dimensions and count
        aggregations = [
            # By location and gender
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'gender']).size(),
            # By location and age group
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'age_group']).size(),
            # By location and education level
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'education__level']).size(),
            # By location and religion
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'religion']).size(),
            # By location and ethnicity
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'ethnicity']).size()
        ]
        
        # Clear existing data for today
        DemographicStats.objects.filter(stat_date=self.today, **filters).delete()
        
        # Save aggregated data
        for agg in aggregations:
            for index, count in agg.items():
                # Unpack the index based on its structure
                if len(index) == 4:  # Location + 1 dimension
                    state_id, lga_id, ward_id, dimension_value = index
                    dimension_name = agg.index.names[3]
                    
                    # Map dimension name to the correct field
                    field_mapping = {
                        'gender': {'gender': dimension_value},
                        'age_group': {'age_group': dimension_value},
                        'education__level': {'education_level': dimension_value},
                        'religion': {'religion': dimension_value},
                        'ethnicity': {'ethnicity': dimension_value}
                    }
                    
                    # Create stat record
                    DemographicStats.objects.create(
                        stat_date=self.today,
                        state_id=state_id,
                        lga_id=lga_id,
                        ward_id=ward_id,
                        count=count,
                        **field_mapping.get(dimension_name, {})
                    )
        
        # Calculate percentages
        self._calculate_percentages(DemographicStats, self.today, filters)
        
        # Update report metadata
        self._update_report_metadata("demographic_aggregation", start_time)
    
    def aggregate_occupations(self, state_id=None, lga_id=None):
        """
        Aggregate occupation data
        """
        start_time = timezone.now()
        
        # Build filter conditions
        filters = {}
        if state_id:
            filters['residence_state_id'] = state_id
        if lga_id:
            filters['residence_lga_id'] = lga_id
        
        # Get citizens with occupation data
        citizens = Citizen.objects.filter(**filters).select_related('occupation')
        
        # Use pandas for efficient aggregation
        df = pd.DataFrame(list(citizens.values(
            'residence_state_id', 'residence_lga_id', 'residence_ward_id',
            'occupation__sector', 'occupation__employment_status', 
            'occupation__income_level', 'occupation__qualification'
        )))
        
        # Group by different dimensions and count
        aggregations = [
            # By location and sector
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'occupation__sector']).size(),
            # By location and employment status
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'occupation__employment_status']).size(),
            # By location and income level
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'occupation__income_level']).size(),
            # By location and qualification
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'occupation__qualification']).size()
        ]
        
        # Clear existing data for today
        OccupationStats.objects.filter(stat_date=self.today, **filters).delete()
        
        # Save aggregated data
        for agg in aggregations:
            for index, count in agg.items():
                # Unpack the index based on its structure
                if len(index) == 4:  # Location + 1 dimension
                    state_id, lga_id, ward_id, dimension_value = index
                    dimension_name = agg.index.names[3]
                    
                    # Map dimension name to the correct field
                    field_mapping = {
                        'occupation__sector': {'occupation_sector': dimension_value},
                        'occupation__employment_status': {'employment_status': dimension_value},
                        'occupation__income_level': {'income_level': dimension_value},
                        'occupation__qualification': {'qualification_level': dimension_value}
                    }
                    
                    # Create stat record
                    OccupationStats.objects.create(
                        stat_date=self.today,
                        state_id=state_id,
                        lga_id=lga_id,
                        ward_id=ward_id,
                        count=count,
                        **field_mapping.get(dimension_name, {})
                    )
        
        # Calculate percentages
        self._calculate_percentages(OccupationStats, self.today, filters)
        
        # Update report metadata
        self._update_report_metadata("occupation_aggregation", start_time)
    
    def aggregate_healthcare(self, state_id=None, lga_id=None):
        """
        Aggregate healthcare data
        """
        start_time = timezone.now()
        
        # Build filter conditions
        filters = {}
        if state_id:
            filters['residence_state_id'] = state_id
        if lga_id:
            filters['residence_lga_id'] = lga_id
        
        # Get citizens with health data
        citizens = Citizen.objects.filter(**filters).select_related('health')
        
        # Use pandas for efficient aggregation
        df = pd.DataFrame(list(citizens.values(
            'residence_state_id', 'residence_lga_id', 'residence_ward_id',
            'health__condition', 'health__disability', 'health__blood_group',
            'health__immunization_status'
        )))
        
        # Group by different dimensions and count
        aggregations = [
            # By location and health condition
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'health__condition']).size(),
            # By location and disability
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'health__disability']).size(),
            # By location and blood group
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'health__blood_group']).size(),
            # By location and immunization status
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'health__immunization_status']).size()
        ]
        
        # Clear existing data for today
        HealthcareStats.objects.filter(stat_date=self.today, **filters).delete()
        
        # Save aggregated data
        for agg in aggregations:
            for index, count in agg.items():
                # Unpack the index based on its structure
                if len(index) == 4:  # Location + 1 dimension
                    state_id, lga_id, ward_id, dimension_value = index
                    dimension_name = agg.index.names[3]
                    
                    # Map dimension name to the correct field
                    field_mapping = {
                        'health__condition': {'health_condition': dimension_value},
                        'health__disability': {'disability_type': dimension_value},
                        'health__blood_group': {'blood_group': dimension_value},
                        'health__immunization_status': {'immunization_status': dimension_value}
                    }
                    
                    # Create stat record
                    HealthcareStats.objects.create(
                        stat_date=self.today,
                        state_id=state_id,
                        lga_id=lga_id,
                        ward_id=ward_id,
                        count=count,
                        **field_mapping.get(dimension_name, {})
                    )
        
        # Calculate percentages
        self._calculate_percentages(HealthcareStats, self.today, filters)
        
        # Update report metadata
        self._update_report_metadata("healthcare_aggregation", start_time)
    
    def aggregate_family_structures(self, state_id=None, lga_id=None):
        """
        Aggregate family structure data
        """
        start_time = timezone.now()
        
        # Build filter conditions
        filters = {}
        if state_id:
            filters['residence_state_id'] = state_id
        if lga_id:
            filters['residence_lga_id'] = lga_id
        
        # Get citizens with family data
        citizens = Citizen.objects.filter(**filters).select_related('family')
        
        # Use pandas for efficient aggregation
        df = pd.DataFrame(list(citizens.values(
            'residence_state_id', 'residence_lga_id', 'residence_ward_id',
            'family__household_size', 'family__marital_status', 
            'family__children_count', 'family__family_type'
        )))
        
        # Create household size groups
        df['household_size_group'] = pd.cut(
            df['family__household_size'],
            bins=[0, 1, 2, 4, 6, 10, 20],
            labels=['1', '2', '3-4', '5-6', '7-10', '10+']
        )
        
        # Create children count groups
        df['children_count_group'] = pd.cut(
            df['family__children_count'],
            bins=[-1, 0, 1, 2, 3, 5, 10, 20],
            labels=['0', '1', '2', '3', '4-5', '6-10', '10+']
        )
        
        # Group by different dimensions and count
        aggregations = [
            # By location and household size
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'household_size_group']).size(),
            # By location and marital status
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'family__marital_status']).size(),
            # By location and children count
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'children_count_group']).size(),
            # By location and family type
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'family__family_type']).size()
        ]
        
        # Clear existing data for today
        FamilyStats.objects.filter(stat_date=self.today, **filters).delete()
        
        # Save aggregated data
        for agg in aggregations:
            for index, count in agg.items():
                # Unpack the index based on its structure
                if len(index) == 4:  # Location + 1 dimension
                    state_id, lga_id, ward_id, dimension_value = index
                    dimension_name = agg.index.names[3]
                    
                    # Map dimension name to the correct field
                    field_mapping = {
                        'household_size_group': {'household_size': dimension_value},
                        'family__marital_status': {'marital_status': dimension_value},
                        'children_count_group': {'children_count': dimension_value},
                        'family__family_type': {'family_type': dimension_value}
                    }
                    
                    # Create stat record
                    FamilyStats.objects.create(
                        stat_date=self.today,
                        state_id=state_id,
                        lga_id=lga_id,
                        ward_id=ward_id,
                        count=count,
                        **field_mapping.get(dimension_name, {})
                    )
        
        # Calculate percentages
        self._calculate_percentages(FamilyStats, self.today, filters)
        
        # Update report metadata
        self._update_report_metadata("family_structure_aggregation", start_time)
    
    def aggregate_interests(self, state_id=None, lga_id=None):
        """
        Aggregate interests and sports data
        """
        start_time = timezone.now()
        
        # Build filter conditions
        filters = {}
        if state_id:
            filters['residence_state_id'] = state_id
        if lga_id:
            filters['residence_lga_id'] = lga_id
        
        # Get citizens with interest data
        citizens = Citizen.objects.filter(**filters).prefetch_related('interests')
        
        # Collect all interests
        interest_data = []
        for citizen in citizens:
            for interest in citizen.interests.all():
                interest_data.append({
                    'residence_state_id': citizen.residence_state_id,
                    'residence_lga_id': citizen.residence_lga_id,
                    'residence_ward_id': citizen.residence_ward_id,
                    'interest_type': interest.interest_type,
                    'sport_name': interest.sport_name if interest.interest_type == 'Sport' else None,
                    'cultural_activity': interest.cultural_activity if interest.interest_type == 'Cultural' else None
                })
        
        # Convert to DataFrame
        df = pd.DataFrame(interest_data)
        
        # Group by different dimensions and count
        aggregations = [
            # By location and interest type
            df.groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'interest_type']).size(),
            # By location and sport name (for sports only)
            df[df['interest_type'] == 'Sport'].groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'sport_name']).size(),
            # By location and cultural activity (for cultural only)
            df[df['interest_type'] == 'Cultural'].groupby(['residence_state_id', 'residence_lga_id', 'residence_ward_id', 'cultural_activity']).size()
        ]
        
        # Clear existing data for today
        InterestStats.objects.filter(stat_date=self.today, **filters).delete()
        
        # Save aggregated data
        for agg in aggregations:
            for index, count in agg.items():
                # Unpack the index based on its structure
                if len(index) == 4:  # Location + 1 dimension
                    state_id, lga_id, ward_id, dimension_value = index
                    dimension_name = agg.index.names[3]
                    
                    # Map dimension name to the correct field
                    field_mapping = {
                        'interest_type': {'interest_type': dimension_value},
                        'sport_name': {'sport_name': dimension_value},
                        'cultural_activity': {'cultural_activity': dimension_value}
                    }
                    
                    # Create stat record
                    InterestStats.objects.create(
                        stat_date=self.today,
                        state_id=state_id,
                        lga_id=lga_id,
                        ward_id=ward_id,
                        count=count,
                        **field_mapping.get(dimension_name, {})
                    )
        
        # Calculate percentages
        self._calculate_percentages(InterestStats, self.today, filters)
        
        # Update report metadata
        self._update_report_metadata("interest_aggregation", start_time)
    
    def _calculate_percentages(self, model, stat_date, filters):
        """
        Calculate percentages for each group
        """
        # Get total counts for each location
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT state_id, lga_id, ward_id, SUM(count) as total
                FROM {model._meta.db_table}
                WHERE stat_date = %s
                GROUP BY state_id, lga_id, ward_id
            """, [stat_date])
            
            totals = {}
            for row in cursor.fetchall():
                state_id, lga_id, ward_id, total = row
                key = (state_id, lga_id, ward_id)
                totals[key] = total
        
        # Update percentages
        for key, total in totals.items():
            state_id, lga_id, ward_id = key
            
            # Build filter for this location
            location_filter = {'stat_date': stat_date}
            if state_id:
                location_filter['state_id'] = state_id
            if lga_id:
                location_filter['lga_id'] = lga_id
            if ward_id:
                location_filter['ward_id'] = ward_id
            
            # Update all records for this location
            model.objects.filter(**location_filter).update(
                percentage=models.F('count') * 100.0 / total
            )
    
    def _update_report_metadata(self, report_name, start_time=None):
        """
        Update report metadata
        """
        if start_time:
            duration = (timezone.now() - start_time).total_seconds()
        else:
            duration = None
        
        # Update or create metadata
        ReportMetadata.objects.update_or_create(
            report_name=report_name,
            defaults={
                'last_generated': timezone.now(),
                'generation_duration': duration,
                'is_cached': True,
                'cache_expiry': timezone.now() + timedelta(days=1)
            }
        )
```

### 4.3 Report Generation Service

```python
# report_generator.py
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
    
    # Additional report generation methods for healthcare, family, and interests would follow a similar pattern
    
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
```

### 4.4 API Endpoints

```python
# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
import json
import csv
from io import StringIO
from .models import (
    DemographicStats, OccupationStats, HealthcareStats, 
    FamilyStats, InterestStats, ReportMetadata, CustomReport
)
from .serializers import (
    DemographicStatsSerializer, OccupationStatsSerializer, 
    HealthcareStatsSerializer, FamilyStatsSerializer, 
    InterestStatsSerializer, ReportMetadataSerializer,
    CustomReportSerializer
)
from .data_aggregator import DataAggregator
from .report_generator import ReportGenerator

class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for generating and retrieving reports
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def demographic(self, request):
        """
        Generate demographic report
        """
        # Get parameters
        state_id = request.query_params.get('state_id')
        lga_id = request.query_params.get('lga_id')
        report_date = request.query_params.get('report_date')
        
        if report_date:
            try:
                report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Generate report
        report_generator = ReportGenerator()
        result = report_generator.generate_demographic_report(
            state_id=state_id,
            lga_id=lga_id,
            report_date=report_date
        )
        
        if result['success']:
            return Response(result['report'])
        else:
            return Response(
                {'error': result['message']},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def occupation(self, request):
        """
        Generate occupation/career report
        """
        # Get parameters
        state_id = request.query_params.get('state_id')
        lga_id = request.query_params.get('lga_id')
        report_date = request.query_params.get('report_date')
        
        if report_date:
            try:
                report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Generate report
        report_generator = ReportGenerator()
        result = report_generator.generate_occupation_report(
            state_id=state_id,
            lga_id=lga_id,
            report_date=report_date
        )
        
        if result['success']:
            return Response(result['report'])
        else:
            return Response(
                {'error': result['message']},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def healthcare(self, request):
        """
        Generate healthcare report
        """
        # Implementation similar to demographic and occupation reports
        pass
    
    @action(detail=False, methods=['get'])
    def family(self, request):
        """
        Generate family structure report
        """
        # Implementation similar to demographic and occupation reports
        pass
    
    @action(detail=False, methods=['get'])
    def interests(self, request):
        """
        Generate interests and sports report
        """
        # Implementation similar to demographic and occupation reports
        pass
    
    @action(detail=False, methods=['get'])
    def executive_dashboard(self, request):
        """
        Generate executive dashboard
        """
        # Get parameters
        state_id = request.query_params.get('state_id')
        report_date = request.query_params.get('report_date')
        
        if report_date:
            try:
                report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Generate dashboard
        report_generator = ReportGenerator()
        result = report_generator.generate_executive_dashboard(
            state_id=state_id,
            report_date=report_date
        )
        
        if result['success']:
            return Response(result['dashboard'])
        else:
            return Response(
                {'error': result['message']},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def run_aggregation(self, request):
        """
        Run data aggregation process
        """
        # Check if user has permission
        if not request.user.has_permission('generate_reports'):
            return Response(
                {'error': 'You do not have permission to run data aggregation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get parameters
        state_id = request.data.get('state_id')
        lga_id = request.data.get('lga_id')
        
        # Run aggregation
        aggregator = DataAggregator()
        
        if state_id and lga_id:
            # Aggregate for specific LGA
            aggregator.aggregate_demographics(state_id=state_id, lga_id=lga_id)
            aggregator.aggregate_occupations(state_id=state_id, lga_id=lga_id)
            aggregator.aggregate_healthcare(state_id=state_id, lga_id=lga_id)
            aggregator.aggregate_family_structures(state_id=state_id, lga_id=lga_id)
            aggregator.aggregate_interests(state_id=state_id, lga_id=lga_id)
        elif state_id:
            # Aggregate for specific state
            aggregator.aggregate_demographics(state_id=state_id)
            aggregator.aggregate_occupations(state_id=state_id)
            aggregator.aggregate_healthcare(state_id=state_id)
            aggregator.aggregate_family_structures(state_id=state_id)
            aggregator.aggregate_interests(state_id=state_id)
        else:
            # Aggregate all data
            aggregator.aggregate_all_data()
        
        return Response({
            'message': 'Data aggregation completed successfully',
            'timestamp': timezone.now()
        })
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        Export report data as CSV
        """
        # Get parameters
        report_type = request.query_params.get('type')
        state_id = request.query_params.get('state_id')
        lga_id = request.query_params.get('lga_id')
        report_date = request.query_params.get('report_date', timezone.now().date().isoformat())
        
        if not report_type:
            return Response(
                {'error': 'Report type is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build filter conditions
        filters = {'stat_date': report_date}
        if state_id:
            filters['state_id'] = state_id
        if lga_id:
            filters['lga_id'] = lga_id
        
        # Get data based on report type
        if report_type == 'demographic':
            data = DemographicStats.objects.filter(**filters)
            serializer = DemographicStatsSerializer
        elif report_type == 'occupation':
            data = OccupationStats.objects.filter(**filters)
            serializer = OccupationStatsSerializer
        elif report_type == 'healthcare':
            data = HealthcareStats.objects.filter(**filters)
            serializer = HealthcareStatsSerializer
        elif report_type == 'family':
            data = FamilyStats.objects.filter(**filters)
            serializer = FamilyStatsSerializer
        elif report_type == 'interests':
            data = InterestStats.objects.filter(**filters)
            serializer = InterestStatsSerializer
        else:
            return Response(
                {'error': f'Invalid report type: {report_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serialize data
        serialized_data = serializer(data, many=True).data
        
        # Create CSV
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=serialized_data[0].keys() if serialized_data else [])
        writer.writeheader()
        writer.writerows(serialized_data)
        
        # Create response
        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{report_date}.csv"'
        
        return response

class CustomReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing custom reports
    """
    queryset = CustomReport.objects.all()
    serializer_class = CustomReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter reports based on user's access
        """
        user = self.request.user
        
        # Super admin can see all reports
        if user.role.name == 'Super Administrator':
            return CustomReport.objects.all()
        
        # Others can only see their own reports
        return CustomReport.objects.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Execute a custom report
        """
        # Get parameters
        parameters = request.data.get('parameters', {})
        
        # Execute report
        report_generator = ReportGenerator()
        result = report_generator.execute_custom_report(pk, parameters)
        
        if result['success']:
            return Response(result['report'])
        else:
            return Response(
                {'error': result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def export_csv(self, request, pk=None):
        """
        Export custom report as CSV
        """
        # Get parameters
        parameters = json.loads(request.query_params.get('parameters', '{}'))
        
        # Execute report
        report_generator = ReportGenerator()
        result = report_generator.execute_custom_report(pk, parameters)
        
        if not result['success']:
            return Response(
                {'error': result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get report data
        report = result['report']
        
        # Create CSV
        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=report['columns'])
        writer.writeheader()
        writer.writerows(report['data'])
        
        # Create response
        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report["title"].replace(" ", "_").lower()}_{timezone.now().date().isoformat()}.csv"'
        
        return response
```

### 4.5 Frontend Dashboard Components

```jsx
// ExecutiveDashboard.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, Row, Col, Statistic, Select, DatePicker, Spin, Alert } from 'antd';
import { UserOutlined, BriefcaseOutlined, HomeOutlined } from '@ant-design/icons';

const { Option } = Select;

const ExecutiveDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState(null);
  const [reportDate, setReportDate] = useState(null);

  useEffect(() => {
    // Fetch states
    const fetchStates = async () => {
      try {
        const response = await axios.get('/api/location/states/');
        setStates(response.data);
      } catch (err) {
        console.error('Error fetching states:', err);
      }
    };

    fetchStates();
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params = {};
      if (selectedState) params.state_id = selectedState;
      if (reportDate) params.report_date = reportDate.format('YYYY-MM-DD');

      const response = await axios.get('/api/reports/executive_dashboard/', { params });
      setDashboard(response.data);
    } catch (err) {
      setError('Failed to load dashboard data. Please try again later.');
      console.error('Error fetching dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStateChange = (value) => {
    setSelectedState(value);
  };

  const handleDateChange = (date) => {
    setReportDate(date);
  };

  const handleApplyFilters = () => {
    fetchDashboard();
  };

  const getIconForMetric = (iconName) => {
    switch (iconName) {
      case 'users':
        return <UserOutlined />;
      case 'briefcase':
        return <BriefcaseOutlined />;
      case 'home':
        return <HomeOutlined />;
      default:
        return null;
    }
  };

  return (
    <div className="executive-dashboard">
      <h1>Executive Dashboard</h1>
      
      <div className="dashboard-filters">
        <Row gutter={16} align="middle">
          <Col>
            <label>State:</label>
            <Select
              style={{ width: 200, marginLeft: 8 }}
              placeholder="Select State"
              allowClear
              onChange={handleStateChange}
              value={selectedState}
            >
              {states.map(state => (
                <Option key={state.id} value={state.id}>{state.name}</Option>
              ))}
            </Select>
          </Col>
          
          <Col>
            <label>Report Date:</label>
            <DatePicker
              style={{ marginLeft: 8 }}
              onChange={handleDateChange}
              value={reportDate}
            />
          </Col>
          
          <Col>
            <button
              className="btn-primary"
              onClick={handleApplyFilters}
            >
              Apply Filters
            </button>
          </Col>
        </Row>
      </div>
      
      {loading ? (
        <div className="loading-container">
          <Spin size="large" />
          <p>Loading dashboard data...</p>
        </div>
      ) : error ? (
        <Alert type="error" message={error} />
      ) : dashboard ? (
        <div className="dashboard-content">
          <Row gutter={16} className="metric-cards">
            {dashboard.metrics.map((metric, index) => (
              <Col span={8} key={index}>
                <Card>
                  <Statistic
                    title={metric.name}
                    value={metric.value}
                    prefix={getIconForMetric(metric.icon)}
                  />
                </Card>
              </Col>
            ))}
          </Row>
          
          <Row gutter={16} className="chart-cards">
            {dashboard.charts.map((chart, index) => (
              <Col span={12} key={index}>
                <Card title={chart.title}>
                  <img
                    src={`data:image/png;base64,${chart.image}`}
                    alt={chart.title}
                    style={{ width: '100%' }}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      ) : (
        <Alert type="info" message="No dashboard data available. Please select filters and apply." />
      )}
    </div>
  );
};

export default ExecutiveDashboard;
```

```jsx
// DemographicReport.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, Row, Col, Select, DatePicker, Spin, Alert, Table, Button } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';

const { Option } = Select;

const DemographicReport = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [states, setStates] = useState([]);
  const [lgas, setLgas] = useState([]);
  const [selectedState, setSelectedState] = useState(null);
  const [selectedLga, setSelectedLga] = useState(null);
  const [reportDate, setReportDate] = useState(null);

  useEffect(() => {
    // Fetch states
    const fetchStates = async () => {
      try {
        const response = await axios.get('/api/location/states/');
        setStates(response.data);
      } catch (err) {
        console.error('Error fetching states:', err);
      }
    };

    fetchStates();
    fetchReport();
  }, []);

  useEffect(() => {
    // Fetch LGAs when state changes
    if (selectedState) {
      const fetchLgas = async () => {
        try {
          const response = await axios.get(`/api/location/lgas/?state_id=${selectedState}`);
          setLgas(response.data);
        } catch (err) {
          console.error('Error fetching LGAs:', err);
        }
      };

      fetchLgas();
      setSelectedLga(null);
    } else {
      setLgas([]);
      setSelectedLga(null);
    }
  }, [selectedState]);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params = {};
      if (selectedState) params.state_id = selectedState;
      if (selectedLga) params.lga_id = selectedLga;
      if (reportDate) params.report_date = reportDate.format('YYYY-MM-DD');

      const response = await axios.get('/api/reports/demographic/', { params });
      setReport(response.data);
    } catch (err) {
      setError('Failed to load report data. Please try again later.');
      console.error('Error fetching report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStateChange = (value) => {
    setSelectedState(value);
  };

  const handleLgaChange = (value) => {
    setSelectedLga(value);
  };

  const handleDateChange = (date) => {
    setReportDate(date);
  };

  const handleApplyFilters = () => {
    fetchReport();
  };

  const handleExportCsv = () => {
    // Build query parameters
    const params = {};
    if (selectedState) params.state_id = selectedState;
    if (selectedLga) params.lga_id = selectedLga;
    if (reportDate) params.report_date = reportDate.format('YYYY-MM-DD');
    
    // Add report type
    params.type = 'demographic';
    
    // Generate URL with query parameters
    const queryString = Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
    
    // Open export URL in new tab
    window.open(`/api/reports/export_csv/?${queryString}`, '_blank');
  };

  return (
    <div className="demographic-report">
      <h1>Demographic Report</h1>
      
      <div className="report-filters">
        <Row gutter={16} align="middle">
          <Col>
            <label>State:</label>
            <Select
              style={{ width: 200, marginLeft: 8 }}
              placeholder="Select State"
              allowClear
              onChange={handleStateChange}
              value={selectedState}
            >
              {states.map(state => (
                <Option key={state.id} value={state.id}>{state.name}</Option>
              ))}
            </Select>
          </Col>
          
          <Col>
            <label>LGA:</label>
            <Select
              style={{ width: 200, marginLeft: 8 }}
              placeholder="Select LGA"
              allowClear
              disabled={!selectedState}
              onChange={handleLgaChange}
              value={selectedLga}
            >
              {lgas.map(lga => (
                <Option key={lga.id} value={lga.id}>{lga.name}</Option>
              ))}
            </Select>
          </Col>
          
          <Col>
            <label>Report Date:</label>
            <DatePicker
              style={{ marginLeft: 8 }}
              onChange={handleDateChange}
              value={reportDate}
            />
          </Col>
          
          <Col>
            <Button
              type="primary"
              onClick={handleApplyFilters}
            >
              Apply Filters
            </Button>
          </Col>
          
          <Col>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExportCsv}
              disabled={!report}
            >
              Export CSV
            </Button>
          </Col>
        </Row>
      </div>
      
      {loading ? (
        <div className="loading-container">
          <Spin size="large" />
          <p>Loading report data...</p>
        </div>
      ) : error ? (
        <Alert type="error" message={error} />
      ) : report ? (
        <div className="report-content">
          {report.sections.map((section, index) => (
            <Card title={section.title} key={index} className="report-section">
              <Row gutter={16}>
                <Col span={12}>
                  <img
                    src={`data:image/png;base64,${section.chart}`}
                    alt={section.title}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col span={12}>
                  <Table
                    dataSource={section.data}
                    rowKey={(record, index) => index}
                    pagination={false}
                    size="small"
                    columns={Object.keys(section.data[0]).map(key => ({
                      title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                      dataIndex: key,
                      key: key,
                      render: (text, record) => {
                        if (key === 'avg_percentage') {
                          return `${parseFloat(text).toFixed(2)}%`;
                        }
                        return text;
                      }
                    }))}
                  />
                </Col>
              </Row>
            </Card>
          ))}
        </div>
      ) : (
        <Alert type="info" message="No report data available. Please select filters and apply." />
      )}
    </div>
  );
};

export default DemographicReport;
```

## 5. Scheduled Tasks

### 5.1 Daily Aggregation Job

```python
# tasks.py
from celery import shared_task
from django.utils import timezone
from .data_aggregator import DataAggregator
import logging

logger = logging.getLogger(__name__)

@shared_task
def aggregate_daily_data():
    """
    Daily task to aggregate citizen data for reporting
    """
    logger.info(f"Starting daily data aggregation at {timezone.now()}")
    
    try:
        # Create aggregator
        aggregator = DataAggregator()
        
        # Run aggregation
        aggregator.aggregate_all_data()
        
        logger.info(f"Daily data aggregation completed successfully at {timezone.now()}")
        return True
    except Exception as e:
        logger.error(f"Error in daily data aggregation: {str(e)}")
        return False
```

### 5.2 Celery Configuration

```python
# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citizen_registration.settings')

app = Celery('citizen_registration')

# Use string names for configuration to avoid pickle issues
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'daily-data-aggregation': {
        'task': 'reporting.tasks.aggregate_daily_data',
        'schedule': crontab(hour=1, minute=0),  # Run at 1:00 AM every day
    },
}
```

## 6. Testing Strategy

### 6.1 Unit Testing

- Test data aggregation functions
- Test report generation functions
- Test API endpoints
- Test CSV export functionality

### 6.2 Integration Testing

- Test end-to-end report generation workflow
- Test dashboard rendering with real data
- Test scheduled tasks

### 6.3 Performance Testing

- Test report generation with large datasets
- Test dashboard loading times
- Test CSV export with large datasets

## 7. Security Considerations

### 7.1 Data Access Control

- Reports should only show data that users have permission to access
- Implement jurisdiction-based filtering (state, LGA, ward)
- Validate all parameters to prevent data leakage

### 7.2 Query Security

- Sanitize all user inputs for custom reports
- Implement query timeouts to prevent resource exhaustion
- Use parameterized queries to prevent SQL injection

### 7.3 Data Privacy

- Anonymize sensitive data in reports when appropriate
- Implement data masking for certain fields
- Ensure exported data is properly secured

## 8. Implementation Plan

### 8.1 Phase 1: Core Reporting Infrastructure

1. Implement database schema for analytics
2. Create data aggregation service
3. Set up scheduled aggregation tasks
4. Implement basic report API endpoints

### 8.2 Phase 2: Report Generation

1. Implement demographic reports
2. Implement occupation/career reports
3. Implement healthcare reports
4. Implement family structure reports
5. Implement interests/sports reports

### 8.3 Phase 3: Dashboards and Visualization

1. Create executive dashboard
2. Implement data visualization components
3. Create report export functionality
4. Implement custom report builder
