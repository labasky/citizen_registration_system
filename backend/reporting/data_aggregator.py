from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .models import (
    DemographicStats, OccupationStats, HealthcareStats, 
    FamilyStats, InterestStats, ReportMetadata
)
from citizen.models import Citizen
from django.db import models

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
