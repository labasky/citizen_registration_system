from rest_framework import serializers
from .models import (
    DemographicStats, OccupationStats, HealthcareStats, 
    FamilyStats, InterestStats, ReportMetadata, CustomReport
)

class DemographicStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for demographic statistics
    """
    class Meta:
        model = DemographicStats
        fields = '__all__'

class OccupationStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for occupation statistics
    """
    class Meta:
        model = OccupationStats
        fields = '__all__'

class HealthcareStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for healthcare statistics
    """
    class Meta:
        model = HealthcareStats
        fields = '__all__'

class FamilyStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for family structure statistics
    """
    class Meta:
        model = FamilyStats
        fields = '__all__'

class InterestStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for interests and sports statistics
    """
    class Meta:
        model = InterestStats
        fields = '__all__'

class ReportMetadataSerializer(serializers.ModelSerializer):
    """
    Serializer for report metadata
    """
    class Meta:
        model = ReportMetadata
        fields = '__all__'

class CustomReportSerializer(serializers.ModelSerializer):
    """
    Serializer for custom reports
    """
    class Meta:
        model = CustomReport
        fields = '__all__'
