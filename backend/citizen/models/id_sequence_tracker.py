from django.db import models

class IDSequenceTracker(models.Model):
    """
    Tracks the last used sequence number for each state, LGA, and year combination
    """
    tracker_id = models.AutoField(primary_key=True)
    state_code = models.CharField(max_length=2)
    lga_code = models.CharField(max_length=2)
    year_code = models.CharField(max_length=2)
    last_sequence_number = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('state_code', 'lga_code', 'year_code')
        
    def __str__(self):
        return f"{self.state_code}-{self.lga_code}-{self.year_code}: {self.last_sequence_number}"
