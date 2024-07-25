## Stock Allocations Imports
#--Default imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import ViewByStaffOnlyPermission

#-- serializers



#--Installed Library imports


class ProcessPayloadView(APIView):
    """
    API View to process a JSON payload and call the SA_WO_Allocation stored procedure.
    This endpoint validates the provided parameters, calls the stored procedure, and returns the result as a JSON response.

    Authentication:
        - JWT Authentication
        - Requires the user to be authenticated and have staff permissions.

    Required Payload:
        - woid (string): Work Order ID
        - from_date (string): Start date in YYYY-MM-DD format
        - to_date (string): End date in YYYY-MM-DD format
        - status (integer): Status indicator (0, 1, or 2)
        - userid (string): User ID
        - icompanyid (string): Company ID
        - group_type (string): Group type (e.g., 'B', 'L', 'P')

    Responses:
        - 200: Data processed successfully
        - 400: Invalid input data
        - 401: Unauthorized: Invalid access token
        - 500: Failed to process the data. Please try again later.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Process payload and call stored procedure",
        operation_description="Process a JSON payload and call the SA_WO_Allocation stored procedure.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'woid': openapi.Schema(type=openapi.TYPE_STRING, description='Work Order ID'),
                'from_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='From Date (YYYY-MM-DD)'),
                'to_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='To Date (YYYY-MM-DD)'),
                'status': openapi.Schema(type=openapi.TYPE_INTEGER, description='Status (0, 1, 2)'),
                'userid': openapi.Schema(type=openapi.TYPE_STRING, description='User ID'),
                'icompanyid': openapi.Schema(type=openapi.TYPE_STRING, description='Company ID'),
                'group_type': openapi.Schema(type=openapi.TYPE_STRING, description="Group Type (e.g., 'B', 'L', 'P')"),
            }
        ),
        responses={
            200: 'Data processed successfully',
            400: 'Invalid input data',
            401: 'Unauthorized: Invalid access token',
            500: 'Failed to process the data. Please try again later.'
        },
        tags=['Stock Allocation / Fetch Data']
    )
    def post(self, request):
        """
        Handle POST request to process the JSON payload and call a stored procedure.

        Validates the provided parameters, calls the SA_WO_Allocation stored procedure,
        and returns the result as a JSON response.

        Args:
            request (HttpRequest): The request object containing the JSON payload.

        Returns:
            Response: The data from the stored procedure or an error message.
        """
        payload = request.data
        required_fields = ['woid', 'from_date', 'to_date', 'status', 'userid', 'icompanyid', 'group_type']
        
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return Response({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

        woid = payload.get('woid')
        from_date = payload.get('from_date')
        to_date = payload.get('to_date')
        status_val = payload.get('status')
        userid = payload.get('userid')
        icompanyid = payload.get('icompanyid')
        group_type = payload.get('group_type')

        try:
            with connection.cursor() as cursor:
                cursor.callproc('SA_WO_Allocation', [woid, from_date, to_date, status_val, icompanyid, userid, group_type])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            response_data = {
                "message" : "Success",
                "data" : results
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"Failed to process the data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
