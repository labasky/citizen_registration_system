import re
from datetime import datetime
from django.db import transaction
from .models.id_sequence_tracker import IDSequenceTracker

class CitizenIDGenerator:
    """
    Service for generating unique citizen IDs
    """
    
    def __init__(self):
        self.country_code = "NG"
    
    def generate_id(self, state_code, lga_code):
        """
        Generate a unique citizen ID
        
        Args:
            state_code (str): 2-letter state code
            lga_code (str): 2-letter LGA code
            
        Returns:
            str: The generated citizen ID
        """
        # Get current year code (last 2 digits)
        year_code = datetime.now().strftime("%y")
        
        # Get next sequence number
        sequence_number = self._get_next_sequence_number(state_code, lga_code, year_code)
        
        # Format sequence number to 6 digits
        formatted_sequence = f"{sequence_number:06d}"
        
        # Combine components without check digit
        id_without_check = f"{self.country_code}-{state_code}-{lga_code}-{year_code}-{formatted_sequence}"
        
        # Calculate check digit
        check_digit = self._calculate_check_digit(id_without_check)
        
        # Return complete ID
        return f"{id_without_check}-{check_digit}"
    
    @transaction.atomic
    def _get_next_sequence_number(self, state_code, lga_code, year_code):
        """
        Get the next sequence number for the given state, LGA, and year
        
        Args:
            state_code (str): 2-letter state code
            lga_code (str): 2-letter LGA code
            year_code (str): 2-digit year code
            
        Returns:
            int: The next sequence number
        """
        # Try to get existing tracker
        tracker, created = IDSequenceTracker.objects.get_or_create(
            state_code=state_code,
            lga_code=lga_code,
            year_code=year_code,
            defaults={'last_sequence_number': 0}
        )
        
        # Increment sequence number
        tracker.last_sequence_number += 1
        tracker.save()
        
        return tracker.last_sequence_number
    
    def _calculate_check_digit(self, id_without_check):
        """
        Calculate the check digit using the Luhn algorithm
        
        Args:
            id_without_check (str): ID string without check digit
            
        Returns:
            int: The calculated check digit
        """
        # Extract only numeric characters
        digits = re.sub(r'\D', '', id_without_check)
        
        # Luhn algorithm
        sum = 0
        for i, digit in enumerate(reversed(digits)):
            n = int(digit)
            if i % 2 == 1:  # Odd position (0-indexed from right)
                n *= 2
                if n > 9:
                    n -= 9
            sum += n
        
        # Calculate check digit
        check_digit = (10 - (sum % 10)) % 10
        
        return check_digit
    
    def validate_id(self, citizen_id):
        """
        Validate a citizen ID
        
        Args:
            citizen_id (str): The citizen ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not citizen_id or not isinstance(citizen_id, str):
            return False
        
        # Check format
        pattern = r'^NG-[A-Z]{2}-[A-Z]{2}-\d{2}-\d{6}-\d{1}$'
        if not re.match(pattern, citizen_id):
            return False
        
        # Extract parts
        parts = citizen_id.split('-')
        if len(parts) != 6:
            return False
        
        # Get ID without check digit and the check digit
        id_without_check = '-'.join(parts[:-1])
        provided_check_digit = int(parts[-1])
        
        # Calculate expected check digit
        expected_check_digit = self._calculate_check_digit(id_without_check)
        
        # Compare check digits
        return provided_check_digit == expected_check_digit
