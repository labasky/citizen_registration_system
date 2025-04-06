# Citizen ID Generation System Design

## 1. Overview

The Citizen ID Generation System is a critical component of the Citizen Registration System that creates unique identifiers for each registered citizen. These IDs serve as the primary means of identification within the system and are used for printing physical ID cards. This document outlines the design and implementation of the ID generation system.

## 2. ID Format Specification

### 2.1 ID Structure

The citizen ID will follow this format:
```
NG-SS-LL-YY-NNNNNN-C
```

Where:
- `NG`: Country code for Nigeria (fixed)
- `SS`: 2-digit state code
- `LL`: 2-digit LGA code
- `YY`: 2-digit year of registration
- `NNNNNN`: 6-digit sequential number within the LGA for the year
- `C`: 1-digit check digit for validation

Example: `NG-LA-IK-25-123456-7`

### 2.2 Component Details

#### 2.2.1 Country Code (NG)
- Fixed as "NG" for Nigeria
- Allows for potential future expansion to other countries

#### 2.2.2 State Code (SS)
- 2-letter code representing the state of registration
- Based on standard state codes used in Nigeria
- Examples: LA (Lagos), KN (Kano), AB (Abia)

#### 2.2.3 LGA Code (LL)
- 2-letter code representing the Local Government Area
- Examples: IK (Ikeja), ET (Eti-Osa), MU (Mushin)

#### 2.2.4 Year Code (YY)
- Last 2 digits of the year of registration
- Examples: 25 (for 2025), 26 (for 2026)

#### 2.2.5 Sequential Number (NNNNNN)
- 6-digit sequential number assigned within the LGA for the specific year
- Resets to 000001 at the beginning of each year for each LGA
- Allows for up to 999,999 registrations per LGA per year

#### 2.2.6 Check Digit (C)
- 1-digit number calculated using the Luhn algorithm
- Helps detect errors in the ID number during data entry or transmission
- Provides a simple validation mechanism

## 3. ID Generation Algorithm

### 3.1 Sequential Number Generation

1. When a new citizen is registered, the system retrieves the last used sequential number for the specific LGA and year
2. If no previous registrations exist for the LGA and year, the sequential number starts at 000001
3. Otherwise, the system increments the last used number by 1
4. The system ensures uniqueness by using database transactions to prevent race conditions

### 3.2 Check Digit Calculation

The check digit is calculated using the Luhn algorithm (also known as the "modulus 10" algorithm):

1. Convert the ID components (excluding the check digit) to a single string
2. Remove all non-numeric characters
3. Starting from the rightmost digit, double the value of every second digit
4. If doubling results in a two-digit number, add the digits together
5. Sum all the digits (both doubled and undoubled)
6. The check digit is the number that, when added to this sum, makes it a multiple of 10

### 3.3 ID Generation Process

1. Determine the state and LGA codes based on the citizen's registration location
2. Get the current year code (last two digits of the current year)
3. Generate the next sequential number for the LGA and year
4. Combine the components into the ID format: NG-SS-LL-YY-NNNNNN
5. Calculate the check digit using the Luhn algorithm
6. Append the check digit to complete the ID: NG-SS-LL-YY-NNNNNN-C
7. Verify the uniqueness of the generated ID
8. Assign the ID to the citizen record

## 4. Implementation Details

### 4.1 Database Tables

#### 4.1.1 ID Sequence Tracker Table

```sql
CREATE TABLE id_sequence_trackers (
    tracker_id SERIAL PRIMARY KEY,
    state_code VARCHAR(2) NOT NULL,
    lga_code VARCHAR(2) NOT NULL,
    year_code VARCHAR(2) NOT NULL,
    last_sequence_number INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state_code, lga_code, year_code)
);
```

### 4.2 ID Generation Service

```python
# id_generator.py
import re
from datetime import datetime
from django.db import transaction
from .models import IDSequenceTracker

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
```

### 4.3 ID Sequence Tracker Model

```python
# models.py
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
```

### 4.4 Integration with Citizen Registration

```python
# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Citizen
from .serializers import CitizenSerializer
from .id_generator import CitizenIDGenerator

class CitizenViewSet(viewsets.ModelViewSet):
    queryset = Citizen.objects.all()
    serializer_class = CitizenSerializer
    
    def perform_create(self, serializer):
        # Get state and LGA codes
        state = serializer.validated_data.get('residence_state')
        lga = serializer.validated_data.get('residence_lga')
        
        # Generate unique ID
        id_generator = CitizenIDGenerator()
        unique_id = id_generator.generate_id(state.code, lga.code)
        
        # Save citizen with generated ID
        serializer.save(unique_id=unique_id, created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def validate_id(self, request, pk=None):
        citizen = self.get_object()
        
        # Validate the citizen's ID
        id_generator = CitizenIDGenerator()
        is_valid = id_generator.validate_id(citizen.unique_id)
        
        return Response({
            'unique_id': citizen.unique_id,
            'is_valid': is_valid
        })
```

## 5. ID Card Generation

### 5.1 ID Card Template

The ID card will include the following elements:
- Nigerian coat of arms
- "NIGERIA" text
- "NATIONAL CITIZEN ID" text
- Citizen's photograph
- Citizen's name
- Unique ID number
- Date of birth
- Gender
- Address
- QR code containing the ID number for electronic verification
- Issue date and expiry date
- Citizen's signature
- Security features (watermark, hologram)

### 5.2 QR Code Generation

```python
# qr_generator.py
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

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
```

### 5.3 ID Card Printing Service

```python
# id_card_service.py
from django.template.loader import render_to_string
from django.conf import settings
import os
from weasyprint import HTML
from .qr_generator import generate_qr_code

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
        qr_code_path = self._generate_and_save_qr_code(citizen.unique_id)
        
        # Prepare context for template
        context = {
            'citizen': citizen,
            'qr_code_path': qr_code_path,
            'issue_date': citizen.registration_date.strftime('%d-%m-%Y'),
            'expiry_date': citizen.registration_date.replace(year=citizen.registration_date.year + 10).strftime('%d-%m-%Y')
        }
        
        # Render HTML template
        html_string = render_to_string('id_card_template.html', context)
        
        # Convert HTML to PDF
        html = HTML(string=html_string, base_url=settings.MEDIA_ROOT)
        pdf = html.write_pdf()
        
        return pdf
    
    def _generate_and_save_qr_code(self, unique_id):
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
```

### 5.4 ID Card API Endpoint

```python
# views.py (continued from 4.4)
from django.http import HttpResponse
from .id_card_service import IDCardPrintService

class CitizenViewSet(viewsets.ModelViewSet):
    # ... (previous code from 4.4)
    
    @action(detail=True, methods=['get'])
    def print_id_card(self, request, pk=None):
        citizen = self.get_object()
        
        # Generate ID card PDF
        id_card_service = IDCardPrintService()
        pdf = id_card_service.generate_id_card_pdf(citizen)
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{citizen.unique_id}_id_card.pdf"'
        
        # Log ID card printing
        from auth.models import AuditLog
        AuditLog.objects.create(
            user=request.user,
            action='print_id_card',
            entity_type='citizen',
            entity_id=citizen.id,
            ip_address=self._get_client_ip(request),
            details=f'Printed ID card for citizen: {citizen.unique_id}'
        )
        
        return response
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

## 6. ID Card Template HTML

```html
<!-- templates/id_card_template.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Citizen ID Card</title>
    <style>
        @page {
            size: 85.6mm 53.98mm; /* ID-1 format (standard credit card size) */
            margin: 0;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            width: 85.6mm;
            height: 53.98mm;
            position: relative;
            color: #000;
        }
        .card {
            width: 100%;
            height: 100%;
            position: relative;
            background-color: #fff;
            border: 1px solid #000;
            box-sizing: border-box;
            overflow: hidden;
        }
        .watermark {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: 0.05;
            width: 70%;
            z-index: 0;
        }
        .header {
            display: flex;
            align-items: center;
            padding: 5mm 5mm 2mm 5mm;
            border-bottom: 0.5mm solid #006400;
        }
        .logo {
            width: 8mm;
            height: 8mm;
            margin-right: 3mm;
        }
        .title {
            flex: 1;
        }
        .country {
            font-weight: bold;
            font-size: 3.5mm;
            margin: 0;
            color: #006400;
        }
        .card-type {
            font-size: 2mm;
            margin: 0;
            color: #333;
        }
        .content {
            display: flex;
            padding: 2mm 5mm;
        }
        .photo {
            width: 20mm;
            height: 25mm;
            border: 0.2mm solid #ccc;
            margin-right: 3mm;
        }
        .details {
            flex: 1;
            font-size: 2mm;
        }
        .detail-row {
            margin-bottom: 1mm;
        }
        .label {
            font-weight: bold;
            color: #555;
            display: inline-block;
            width: 10mm;
        }
        .footer {
            display: flex;
            justify-content: space-between;
            padding: 2mm 5mm;
            font-size: 1.8mm;
        }
        .dates {
            display: flex;
            flex-direction: column;
        }
        .signature {
            width: 15mm;
            height: 5mm;
            border-bottom: 0.2mm solid #555;
            text-align: center;
            font-size: 1.5mm;
        }
        .qr-code {
            width: 10mm;
            height: 10mm;
        }
    </style>
</head>
<body>
    <div class="card">
        <!-- Watermark -->
        <img src="{{ MEDIA_URL }}images/nigeria_coat_of_arms.png" class="watermark">
        
        <!-- Header -->
        <div class="header">
            <img src="{{ MEDIA_URL }}images/nigeria_coat_of_arms.png" class="logo">
            <div class="title">
                <p class="country">NIGERIA</p>
                <p class="card-type">NATIONAL CITIZEN ID</p>
            </div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <img src="{{ citizen.photo_url }}" class="photo">
            
            <div class="details">
                <div class="detail-row">
                    <span class="label">Name:</span>
                    <span>{{ citizen.first_name }} {{ citizen.middle_name|first }}. {{ citizen.last_name }}</span>
                </div>
                <div class="detail-row">
                    <span class="label">ID#:</span>
                    <span>{{ citizen.unique_id }}</span>
                </div>
                <div class="detail-row">
                    <span class="label">DOB:</span>
                    <span>{{ citizen.date_of_birth|date:"d-m-Y" }}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Sex:</span>
                    <span>{{ citizen.gender }}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Address:</span>
                    <span>{{ citizen.address|truncatechars:40 }}</span>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="dates">
                <div><span class="label">Issue:</span> {{ issue_date }}</div>
                <div><span class="label">Exp:</span> {{ expiry_date }}</div>
            </div>
            
            <div class="signature">
                Signature
            </div>
            
            <img src="{{ qr_code_path }}" class="qr-code">
        </div>
    </div>
</body>
</html>
```

## 7. Frontend Integration

### 7.1 ID Card Generation Component

```jsx
// IDCardGeneration.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const IDCardGeneration = () => {
  const { citizenId } = useParams();
  const [citizen, setCitizen] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [printerOptions, setPrinterOptions] = useState({
    printer: 'default',
    copies: 1,
    quality: 'high'
  });

  useEffect(() => {
    const fetchCitizen = async () => {
      try {
        const response = await axios.get(`/api/citizens/${citizenId}/`);
        setCitizen(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load citizen data');
        setLoading(false);
      }
    };

    fetchCitizen();
  }, [citizenId]);

  const handlePrinterChange = (e) => {
    setPrinterOptions({
      ...printerOptions,
      [e.target.name]: e.target.value
    });
  };

  const handlePrintIDCard = async () => {
    try {
      // Request ID card PDF
      const response = await axios.get(`/api/citizens/${citizenId}/print_id_card/`, {
        responseType: 'blob'
      });

      // Create blob URL and open in new window
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (err) {
      setError('Failed to generate ID card');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="id-card-container">
      <div className="citizen-info">
        <h2 className="info-title">Citizen Information</h2>
        
        {citizen.photo_url && (
          <img src={citizen.photo_url} alt="Citizen" className="citizen-photo" />
        )}
        
        <div className="info-row">
          <div className="info-label">ID:</div>
          <div className="info-value">{citizen.unique_id}</div>
        </div>
        
        <div className="info-row">
          <div className="info-label">Name:</div>
          <div className="info-value">
            {citizen.first_name} {citizen.middle_name} {citizen.last_name}
          </div>
        </div>
        
        <div className="info-row">
          <div className="info-label">Date of Birth:</div>
          <div className="info-value">
            {new Date(citizen.date_of_birth).toLocaleDateString()}
          </div>
        </div>
        
        <div className="info-row">
          <div className="info-label">Gender:</div>
          <div className="info-value">{citizen.gender}</div>
        </div>
        
        <div className="info-row">
          <div className="info-label">Address:</div>
          <div className="info-value">{citizen.address}</div>
        </div>
        
        <div className="info-row">
          <div className="info-label">LGA:</div>
          <div className="info-value">{citizen.residence_lga.name}</div>
        </div>
        
        <div className="info-row">
          <div className="info-label">State:</div>
          <div className="info-value">{citizen.residence_state.name}</div>
        </div>
      </div>
      
      <div className="card-preview">
        <h2 className="preview-title">ID Card Preview</h2>
        
        <div className="id-card">
          {/* ID Card Preview - simplified version of the actual template */}
          <div className="card-header">
            <div className="card-logo">🇳🇬</div>
            <div className="card-title">
              <p className="card-country">NIGERIA</p>
              <p className="card-type">NATIONAL CITIZEN ID</p>
            </div>
          </div>
          
          <div className="card-content">
            {citizen.photo_url ? (
              <img src={citizen.photo_url} alt="Citizen" className="card-photo" />
            ) : (
              <div className="card-photo">No Photo</div>
            )}
            
            <div className="card-details">
              <div className="card-detail-row">
                <span className="card-label">Name:</span>
                <span>{citizen.first_name} {citizen.middle_name ? citizen.middle_name.charAt(0) + '.' : ''} {citizen.last_name}</span>
              </div>
              <div className="card-detail-row">
                <span className="card-label">ID#:</span>
                <span>{citizen.unique_id}</span>
              </div>
              <div className="card-detail-row">
                <span className="card-label">DOB:</span>
                <span>{new Date(citizen.date_of_birth).toLocaleDateString('en-GB')}</span>
              </div>
              <div className="card-detail-row">
                <span className="card-label">Sex:</span>
                <span>{citizen.gender}</span>
              </div>
              <div className="card-detail-row">
                <span className="card-label">Address:</span>
                <span>{citizen.address.substring(0, 40)}</span>
              </div>
            </div>
          </div>
          
          <div className="card-footer">
            <div className="card-dates">
              <div>
                <span className="card-label">Issue:</span> {new Date().toLocaleDateString('en-GB')}
              </div>
              <div>
                <span className="card-label">Exp:</span> {new Date(new Date().setFullYear(new Date().getFullYear() + 10)).toLocaleDateString('en-GB')}
              </div>
            </div>
            
            <div className="card-signature">
              Signature
            </div>
            
            <div className="card-qr">
              {/* QR code placeholder */}
            </div>
          </div>
        </div>
      </div>
      
      <div className="print-options">
        <h2 className="options-title">Print Options</h2>
        
        <form className="options-form">
          <div className="option-group">
            <label className="option-label">Printer</label>
            <select 
              className="option-select"
              name="printer"
              value={printerOptions.printer}
              onChange={handlePrinterChange}
            >
              <option value="default">Default Printer</option>
              <option value="hp">HP LaserJet Pro</option>
              <option value="epson">Epson ID Card Printer</option>
              <option value="zebra">Zebra Card Printer</option>
            </select>
          </div>
          
          <div className="option-group">
            <label className="option-label">Copies</label>
            <select 
              className="option-select"
              name="copies"
              value={printerOptions.copies}
              onChange={handlePrinterChange}
            >
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
            </select>
          </div>
          
          <div className="option-group">
            <label className="option-label">Quality</label>
            <select 
              className="option-select"
              name="quality"
              value={printerOptions.quality}
              onChange={handlePrinterChange}
            >
              <option value="draft">Draft</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
            </select>
          </div>
        </form>
        
        <div className="form-actions">
          <button className="btn btn-secondary">Cancel</button>
          <button className="btn btn-primary" onClick={handlePrintIDCard}>
            Print ID Card
          </button>
        </div>
      </div>
    </div>
  );
};

export default IDCardGeneration;
```

## 8. Testing Strategy

### 8.1 Unit Testing

- Test ID generation algorithm
- Test check digit calculation
- Test ID validation
- Test sequence number generation
- Test QR code generation

### 8.2 Integration Testing

- Test ID generation during citizen registration
- Test ID card PDF generation
- Test ID card printing workflow

### 8.3 Performance Testing

- Test ID generation under high load
- Test concurrent ID generation to ensure uniqueness

## 9. Security Considerations

### 9.1 ID Tampering Prevention

- Check digit validation to detect manual errors
- QR code for electronic verification
- Watermarks and security features on physical cards
- Audit logging of all ID card printing operations

### 9.2 ID Theft Prevention

- Secure storage of ID information
- Access control for ID card printing
- Expiration dates on ID cards
- Ability to revoke and reissue IDs if compromised

## 10. Implementation Plan

### 10.1 Phase 1: Core ID Generation

1. Implement ID format and structure
2. Create ID sequence tracker
3. Implement ID generation algorithm
4. Integrate with citizen registration

### 10.2 Phase 2: ID Card Generation

1. Design ID card template
2. Implement QR code generation
3. Create PDF generation service
4. Implement ID card printing API

### 10.3 Phase 3: Frontend Integration

1. Create ID card preview component
2. Implement print options interface
3. Connect to backend API
4. Test end-to-end workflow
