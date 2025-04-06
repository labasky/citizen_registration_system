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
from datetime import datetime

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
        result = report_generator.generate_healthcare_report(
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
    def family(self, request):
        """
        Generate family structure report
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
        result = report_generator.generate_family_report(
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
    def interests(self, request):
        """
        Generate interests and sports report
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
        result = report_generator.generate_interests_report(
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
        if not request.user.has_perm('reporting.generate_reports'):
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
