from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models.citizen import Citizen
from .serializers import CitizenSerializer
from .id_generator import CitizenIDGenerator
from .id_card_service import IDCardPrintService
from auth.models import AuditLog

class CitizenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing citizen data and ID card generation
    """
    queryset = Citizen.objects.all()
    serializer_class = CitizenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter citizens based on user's jurisdiction
        """
        user = self.request.user
        
        # Super admin can see all citizens
        if user.role.name == 'Super Administrator':
            return Citizen.objects.all()
        
        # State admin can see citizens in their state
        if user.role.name == 'State Administrator':
            return Citizen.objects.filter(residence_state=user.state)
        
        # LGA admin can see citizens in their LGA
        if user.role.name == 'LGA Administrator':
            return Citizen.objects.filter(
                residence_state=user.state,
                residence_lga=user.lga
            )
        
        # Data entry operator can see citizens in their ward
        return Citizen.objects.filter(
            residence_state=user.state,
            residence_lga=user.lga,
            residence_ward=user.ward
        )
    
    def perform_create(self, serializer):
        """
        Generate unique ID when creating a new citizen
        """
        # Get state and LGA codes
        state = serializer.validated_data.get('residence_state')
        lga = serializer.validated_data.get('residence_lga')
        
        # Generate unique ID
        id_generator = CitizenIDGenerator()
        unique_id = id_generator.generate_id(state.code, lga.code)
        
        # Save citizen with generated ID
        citizen = serializer.save(
            unique_id=unique_id, 
            created_by=self.request.user
        )
        
        # Log citizen creation
        AuditLog.objects.create(
            user=self.request.user,
            action='citizen_create',
            entity_type='citizen',
            entity_id=citizen.id,
            ip_address=self._get_client_ip(self.request),
            details=f'Created citizen with ID: {unique_id}'
        )
    
    def perform_update(self, serializer):
        """
        Log citizen update
        """
        citizen = serializer.save(updated_by=self.request.user)
        
        # Log citizen update
        AuditLog.objects.create(
            user=self.request.user,
            action='citizen_update',
            entity_type='citizen',
            entity_id=citizen.id,
            ip_address=self._get_client_ip(self.request),
            details=f'Updated citizen with ID: {citizen.unique_id}'
        )
    
    def perform_destroy(self, instance):
        """
        Log citizen deletion
        """
        # Log citizen deletion
        AuditLog.objects.create(
            user=self.request.user,
            action='citizen_delete',
            entity_type='citizen',
            entity_id=instance.id,
            ip_address=self._get_client_ip(self.request),
            details=f'Deleted citizen with ID: {instance.unique_id}'
        )
        
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def validate_id(self, request, pk=None):
        """
        Validate a citizen's ID
        """
        citizen = self.get_object()
        
        # Validate the citizen's ID
        id_generator = CitizenIDGenerator()
        is_valid = id_generator.validate_id(citizen.unique_id)
        
        return Response({
            'unique_id': citizen.unique_id,
            'is_valid': is_valid
        })
    
    @action(detail=True, methods=['get'])
    def print_id_card(self, request, pk=None):
        """
        Generate and print an ID card for a citizen
        """
        citizen = self.get_object()
        
        # Generate ID card PDF
        id_card_service = IDCardPrintService()
        pdf = id_card_service.generate_id_card_pdf(citizen)
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{citizen.unique_id}_id_card.pdf"'
        
        # Log ID card printing
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
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
