from django.template.loader import render_to_string
from django.conf import settings
import os
from weasyprint import HTML
from .qr_generator import save_qr_code

class IDCardPrintService:
    """
    Service for generating and printing ID cards
    """
    
    def generate_id_card_pdf(self, citizen):
        """
        Generate a PDF ID card for the citizen
        
        Args:
            citizen: The citizen object
            
        Returns:
            bytes: The generated PDF as bytes
        """
        # Generate QR code
        qr_code_path = save_qr_code(citizen.unique_id)
        
        # Prepare context for template
        context = {
            'citizen': citizen,
            'qr_code_path': qr_code_path,
            'issue_date': citizen.registration_date.strftime('%d-%m-%Y'),
            'expiry_date': citizen.registration_date.replace(year=citizen.registration_date.year + 10).strftime('%d-%m-%Y'),
            'MEDIA_URL': settings.MEDIA_URL
        }
        
        # Render HTML template
        html_string = render_to_string('id_card_template.html', context)
        
        # Convert HTML to PDF
        html = HTML(string=html_string, base_url=settings.MEDIA_ROOT)
        pdf = html.write_pdf()
        
        return pdf
