from rest_framework import viewsets, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import TextMatterChecking
from .serializers import TextMatterCheckingSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import ViewByStaffOnlyPermission
from django.db import connection, DatabaseError
from accounts.helpers import GetUserData
from rest_framework.response import Response


class PageLoadDropdown(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Retrieve data for Page Load API",
        operation_description="This GET API request returns all data related to page load.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='Bearer token (format: Bearer <Token>)',
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(description="Success"),
            401: openapi.Response(description="Unauthorized"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Text Matter Checking']
    )
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # First query to fetch DocID
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT a.DocID FROM item_jobcardmaster_d as a
                    WHERE 
                        a.IcompanyID=%s
                    """, [icompanyid])
                rows = cursor.fetchall()

            results = [
                {
                    'DocID': row[0]
                } 
                for row in rows
            ]

            # Second query to fetch UserID and UserName
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT UserID, UserName FROM usermaster 
                    WHERE Icompanyid=%s
                    """, [icompanyid])
                user_rows = cursor.fetchall()

            user_data_results = [
                {
                    'UserID': user_row[0],
                    'UserName': user_row[1]
                } 
                for user_row in user_rows
            ]

            response_data = {
                "message": "Success",
                "data": {
                    "JobIdDropdown": results,
                    "user_data": user_data_results,
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        except DatabaseError as e:
            return Response({'error': 'Database error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TextMatterCheckingViewSet(viewsets.ModelViewSet):
    queryset = TextMatterChecking.objects.all()
    serializer_class = TextMatterCheckingSerializer

    @swagger_auto_schema(
        operation_summary="List all Text Matter Checkings",
        operation_description="Retrieve a list of all text matter checkings",
        responses={200: TextMatterCheckingSerializer(many=True)},
        tags=['Text Matter Checking']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            "message": "Success",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Retrieve a Text Matter Checking",
        operation_description="Retrieve a text matter checking by JobId",
        manual_parameters=[
            openapi.Parameter(
                'jobid',
                openapi.IN_PATH,
                description="Job ID (format: '10174/Y4/23-24')",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = {
            "message": "Success",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a Text Matter Checking",
        operation_description="Create a new text matter checking",
        request_body=TextMatterCheckingSerializer,
        responses={201: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_data = {
            "message": "Success",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Update a Text Matter Checking",
        operation_description="Update an existing text matter checking",
        manual_parameters=[
            openapi.Parameter(
                'jobid',
                openapi.IN_PATH,
                description="Job ID (format: '10174/Y4/23-24')",
                type=openapi.TYPE_STRING
            )
        ],
        request_body=TextMatterCheckingSerializer,
        responses={200: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {
            "message": "Success",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Partially Update a Text Matter Checking",
        operation_description="Partially update an existing text matter checking",
        manual_parameters=[
            openapi.Parameter(
                'jobid',
                openapi.IN_PATH,
                description="Job ID (format: '10174/Y4/23-24')",
                type=openapi.TYPE_STRING
            )
        ],
        request_body=TextMatterCheckingSerializer,
        responses={200: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)

    @swagger_auto_schema(
        operation_summary="Delete a Text Matter Checking",
        operation_description="Delete a text matter checking by JobId",
        manual_parameters=[
            openapi.Parameter(
                'jobid',
                openapi.IN_PATH,
                description="Job ID (format: '10174/Y4/23-24')",
                type=openapi.TYPE_STRING
            )
        ],
        responses={204: "No Content"},
        tags=['Text Matter Checking']
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        response_data = {
            "message": "Success",
            "data": {}
        }
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
