from django.db import models

class DemographicStats(models.Model):
    """
    Stores aggregated demographic statistics
    """
    stat_id = models.AutoField(primary_key=True)
    stat_date = models.DateField()
    state = models.ForeignKey('location.State', on_delete=models.CASCADE, null=True)
    lga = models.ForeignKey('location.LocalGovernmentArea', on_delete=models.CASCADE, null=True)
    ward = models.ForeignKey('location.Ward', on_delete=models.CASCADE, null=True)
    age_group = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    education_level = models.CharField(max_length=50, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    ethnicity = models.CharField(max_length=50, null=True, blank=True)
    count = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['stat_date']),
            models.Index(fields=['state']),
            models.Index(fields=['lga']),
            models.Index(fields=['ward']),
        ]
        
    def __str__(self):
        return f"Demographic Stats {self.stat_date} - {self.state or 'All'} - {self.lga or 'All'}"

class OccupationStats(models.Model):
    """
    Stores aggregated occupation/career statistics
    """
    stat_id = models.AutoField(primary_key=True)
    stat_date = models.DateField()
    state = models.ForeignKey('location.State', on_delete=models.CASCADE, null=True)
    lga = models.ForeignKey('location.LocalGovernmentArea', on_delete=models.CASCADE, null=True)
    ward = models.ForeignKey('location.Ward', on_delete=models.CASCADE, null=True)
    occupation_sector = models.CharField(max_length=100, null=True, blank=True)
    employment_status = models.CharField(max_length=50, null=True, blank=True)
    income_level = models.CharField(max_length=50, null=True, blank=True)
    qualification_level = models.CharField(max_length=50, null=True, blank=True)
    count = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['stat_date']),
            models.Index(fields=['state']),
            models.Index(fields=['lga']),
            models.Index(fields=['ward']),
        ]
        
    def __str__(self):
        return f"Occupation Stats {self.stat_date} - {self.state or 'All'} - {self.lga or 'All'}"

class HealthcareStats(models.Model):
    """
    Stores aggregated healthcare statistics
    """
    stat_id = models.AutoField(primary_key=True)
    stat_date = models.DateField()
    state = models.ForeignKey('location.State', on_delete=models.CASCADE, null=True)
    lga = models.ForeignKey('location.LocalGovernmentArea', on_delete=models.CASCADE, null=True)
    ward = models.ForeignKey('location.Ward', on_delete=models.CASCADE, null=True)
    health_condition = models.CharField(max_length=100, null=True, blank=True)
    disability_type = models.CharField(max_length=100, null=True, blank=True)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    immunization_status = models.CharField(max_length=50, null=True, blank=True)
    count = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['stat_date']),
            models.Index(fields=['state']),
            models.Index(fields=['lga']),
            models.Index(fields=['ward']),
        ]
        
    def __str__(self):
        return f"Healthcare Stats {self.stat_date} - {self.state or 'All'} - {self.lga or 'All'}"

class FamilyStats(models.Model):
    """
    Stores aggregated family structure statistics
    """
    stat_id = models.AutoField(primary_key=True)
    stat_date = models.DateField()
    state = models.ForeignKey('location.State', on_delete=models.CASCADE, null=True)
    lga = models.ForeignKey('location.LocalGovernmentArea', on_delete=models.CASCADE, null=True)
    ward = models.ForeignKey('location.Ward', on_delete=models.CASCADE, null=True)
    household_size = models.CharField(max_length=20, null=True, blank=True)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    children_count = models.CharField(max_length=20, null=True, blank=True)
    family_type = models.CharField(max_length=50, null=True, blank=True)
    count = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['stat_date']),
            models.Index(fields=['state']),
            models.Index(fields=['lga']),
            models.Index(fields=['ward']),
        ]
        
    def __str__(self):
        return f"Family Stats {self.stat_date} - {self.state or 'All'} - {self.lga or 'All'}"

class InterestStats(models.Model):
    """
    Stores aggregated interests and sports statistics
    """
    stat_id = models.AutoField(primary_key=True)
    stat_date = models.DateField()
    state = models.ForeignKey('location.State', on_delete=models.CASCADE, null=True)
    lga = models.ForeignKey('location.LocalGovernmentArea', on_delete=models.CASCADE, null=True)
    ward = models.ForeignKey('location.Ward', on_delete=models.CASCADE, null=True)
    interest_type = models.CharField(max_length=100, null=True, blank=True)
    sport_name = models.CharField(max_length=100, null=True, blank=True)
    cultural_activity = models.CharField(max_length=100, null=True, blank=True)
    count = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['stat_date']),
            models.Index(fields=['state']),
            models.Index(fields=['lga']),
            models.Index(fields=['ward']),
        ]
        
    def __str__(self):
        return f"Interest Stats {self.stat_date} - {self.state or 'All'} - {self.lga or 'All'}"

class ReportMetadata(models.Model):
    """
    Stores metadata about generated reports
    """
    report_id = models.AutoField(primary_key=True)
    report_name = models.CharField(max_length=100)
    report_description = models.TextField(null=True, blank=True)
    last_generated = models.DateTimeField()
    generation_duration = models.IntegerField(null=True, blank=True)  # in seconds
    is_cached = models.BooleanField(default=False)
    cache_expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.report_name

class CustomReport(models.Model):
    """
    Stores custom report definitions created by users
    """
    custom_report_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    report_name = models.CharField(max_length=100)
    report_description = models.TextField(null=True, blank=True)
    report_query = models.TextField()
    parameters = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.report_name
