import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.conf import settings

def generate_qr_code(data):
    """
    Generate a QR code image for the given data
    
    Args:
        data (str): The data to encode in the QR code
        
    Returns:
        ContentFile: The generated QR code image as a ContentFile
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    # Create ContentFile from BytesIO
    return ContentFile(buffer.getvalue())

def save_qr_code(unique_id):
    """
    Generate and save QR code for the unique ID
    
    Args:
        unique_id (str): The unique ID to encode
        
    Returns:
        str: Path to the saved QR code image
    """
    # Generate QR code
    qr_code = generate_qr_code(unique_id)
    
    # Save QR code to file
    qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
    os.makedirs(qr_code_dir, exist_ok=True)
    
    qr_code_path = os.path.join(qr_code_dir, f"{unique_id.replace('-', '_')}.png")
    
    with open(qr_code_path, 'wb') as f:
        f.write(qr_code.read())
    
    return qr_code_path
