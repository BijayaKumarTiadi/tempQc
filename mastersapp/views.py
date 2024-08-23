from rest_framework import viewsets, status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import TextMatterChecking, Colorcheckingreport
from .serializers import TextMatterCheckingSerializer,ColorcheckingreportSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import ViewByStaffOnlyPermission
from django.db import connection, DatabaseError
from accounts.helpers import GetUserData
from rest_framework.response import Response
from datetime import datetime,timezone


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
                    SELECT a.DocID,b.description as JobName FROM item_jobcardmaster_d as a, item_master AS b
                    WHERE 
                        a.itemid=b.itemid AND b.groupid='00008' AND a.IcompanyID=%s
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

    @swagger_auto_schema(
        operation_summary="Search data based on DocID",
        operation_description="This POST API searches for details based on provided DocID.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='Bearer token (format: Bearer <Token>)',
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'DocID': openapi.Schema(type=openapi.TYPE_STRING, description='Document ID to search for')
                # 'IcompanyID': openapi.Schema(type=openapi.TYPE_STRING, description='Company ID')
            },
            required=['DocID']
        ),
        responses={
            200: openapi.Response(description="Success"),
            400: openapi.Response(description="Bad Request"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Text Matter Checking']
    )

    def post(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid

        docid_pattern = request.data.get('DocID')
        # icompanyid = request.data.get('IcompanyID')

        if not docid_pattern:
            return Response({'error': 'DocID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not icompanyid:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Query to fetch details based on DocID
            with connection.cursor() as cursor:
                # cursor.execute("""
                #     SELECT a.DocID, b.description as JobName FROM item_jobcardmaster_d as a
                #     JOIN item_master AS b ON a.itemid = b.itemid
                #     WHERE a.DocID like '%%s%' AND a.IcompanyID=%s
                #     """, [docid, icompanyid])

                cursor.execute("""
                    SELECT a.DocID, b.description AS JobName FROM item_jobcardmaster_d AS a
                    JOIN item_master AS b ON a.itemid = b.itemid
                    WHERE a.DocID LIKE %s AND a.IcompanyID=%s
                    """, [f'%{docid_pattern}%', icompanyid])
                rows = cursor.fetchall()

            results = [
                {
                    'DocID': row[0],
                    'JobName': row[1]  # Include JobName in results
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
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                "message": "Success",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Retrieve a Text Matter Checking",
        operation_description="Retrieve a text matter checking by AutoId",
        manual_parameters=[
            openapi.Parameter(
                'autoid',
                openapi.IN_PATH,
                description="Auto ID (format: integer)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            response_data = {
                "message": "Success",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Create a Text Matter Checking",
        operation_description="Create a new text matter checking",
        request_body=TextMatterCheckingSerializer,
        responses={201: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def create(self, request, *args, **kwargs):
        try:
            request.data['adatetime'] = datetime.now(timezone.utc)
            request.data['mdatetime'] = datetime(2060, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            response_data = {
                "message": "Success",
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Update a Text Matter Checking",
        operation_description="Update an existing text matter checking",
        manual_parameters=[
            openapi.Parameter(
                'autoid',
                openapi.IN_PATH,
                description="Auto ID (format: integer)",
                type=openapi.TYPE_INTEGER
            )
        ],
        request_body=TextMatterCheckingSerializer,
        responses={200: TextMatterCheckingSerializer()},
        tags=['Text Matter Checking']
    )
    def update(self, request, *args, **kwargs):
        try:
            request.data['mdatetime'] = datetime.now(timezone.utc)
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Partially Update a Text Matter Checking",
        operation_description="Partially update an existing text matter checking",
        manual_parameters=[
            openapi.Parameter(
                'autoid',
                openapi.IN_PATH,
                description="Auto ID (format: integer)",
                type=openapi.TYPE_INTEGER
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
        operation_description="Delete a text matter checking by AutoId",
        manual_parameters=[
            openapi.Parameter(
                'autoid',
                openapi.IN_PATH,
                description="Auto ID (format: integer)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: "ok"},
        tags=['Text Matter Checking']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            response_data = {
                "message": "Data Deleted Successfully",
                "data": {}
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class TextMatterCheckingViewSet(viewsets.ModelViewSet):
#     queryset = TextMatterChecking.objects.all()
#     serializer_class = TextMatterCheckingSerializer

#     @swagger_auto_schema(
#         operation_summary="List all Text Matter Checkings",
#         operation_description="Retrieve a list of all text matter checkings",
#         responses={200: TextMatterCheckingSerializer(many=True)},
#         tags=['Text Matter Checking']
#     )
#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#             response_data = {
#                 "message": "Success",
#                 "data": serializer.data
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     @swagger_auto_schema(
#         operation_summary="Retrieve a Text Matter Checking",
#         operation_description="Retrieve a text matter checking by JobId",
#         manual_parameters=[
#             openapi.Parameter(
#                 'jobid',
#                 openapi.IN_PATH,
#                 description="Job ID (format: '10174/Y4/23-24')",
#                 type=openapi.TYPE_STRING
#             )
#         ],
#         responses={200: TextMatterCheckingSerializer()},
#         tags=['Text Matter Checking']
#     )
#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = self.get_serializer(instance)
#             response_data = {
#                 "message": "Success",
#                 "data": serializer.data
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     @swagger_auto_schema(
#         operation_summary="Create a Text Matter Checking",
#         operation_description="Create a new text matter checking",
#         request_body=TextMatterCheckingSerializer,
#         responses={201: TextMatterCheckingSerializer()},
#         tags=['Text Matter Checking']
#     )
#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             response_data = {
#                 "message": "Success",
#                 "data": serializer.data
#             }
#             return Response(response_data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     @swagger_auto_schema(
#         operation_summary="Update a Text Matter Checking",
#         operation_description="Update an existing text matter checking",
#         manual_parameters=[
#             openapi.Parameter(
#                 'jobid',
#                 openapi.IN_PATH,
#                 description="Job ID (format: '10174/Y4/23-24')",
#                 type=openapi.TYPE_STRING
#             )
#         ],
#         request_body=TextMatterCheckingSerializer,
#         responses={200: TextMatterCheckingSerializer()},
#         tags=['Text Matter Checking']
#     )
#     def update(self, request, *args, **kwargs):
#         try:
#             partial = kwargs.pop('partial', False)
#             instance = self.get_object()
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             response_data = {
#                 "message": "Success",
#                 "data": serializer.data
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     @swagger_auto_schema(
#         operation_summary="Partially Update a Text Matter Checking",
#         operation_description="Partially update an existing text matter checking",
#         manual_parameters=[
#             openapi.Parameter(
#                 'jobid',
#                 openapi.IN_PATH,
#                 description="Job ID (format: '10174/Y4/23-24')",
#                 type=openapi.TYPE_STRING
#             )
#         ],
#         request_body=TextMatterCheckingSerializer,
#         responses={200: TextMatterCheckingSerializer()},
#         tags=['Text Matter Checking']
#     )
#     def partial_update(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs, partial=True)

#     @swagger_auto_schema(
#         operation_summary="Delete a Text Matter Checking",
#         operation_description="Delete a text matter checking by JobId",
#         manual_parameters=[
#             openapi.Parameter(
#                 'jobid',
#                 openapi.IN_PATH,
#                 description="Job ID (format: '10174/Y4/23-24')",
#                 type=openapi.TYPE_STRING
#             )
#         ],
#         responses={200: "ok"},
#         tags=['Text Matter Checking']
#     )
#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             response_data = {
#                 "message": "Data Deleted Successfully",
#                 "data": {}
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



"""
    Colore Checking Form API
"""

class ColorcheckingreportAPIView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve all Color Checking Reports or a specific one",
        operation_description="This GET API request returns all color checking reports or a specific one if a primary key is provided.",
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
            404: openapi.Response(description="Not Found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Color Checking Report']
    )
    def get(self, request, pk=None):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if pk:
                report = Colorcheckingreport.objects.get(pk=pk)
                serializer = ColorcheckingreportSerializer(report)
            else:
                reports = Colorcheckingreport.objects.all()
                serializer = ColorcheckingreportSerializer(reports, many=True)

            response_data = {
                "message": "Success",
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Colorcheckingreport.DoesNotExist:
            return Response({'error': 'Colorcheckingreport not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Create a new Color Checking Report",
        operation_description="This POST API request creates a new color checking report.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='Bearer token (format: Bearer <Token>)',
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        request_body=ColorcheckingreportSerializer,
        responses={
            201: openapi.Response(description="Created"),
            400: openapi.Response(description="Bad Request"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Color Checking Report']
    )
    def post(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            request.data['adatetime'] = datetime.now(timezone.utc)
            # request.data['mdatetime'] = datetime.now(timezone.utc)
            request.data['mdatetime'] = datetime(1990, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            print(request.data)
            serializer = ColorcheckingreportSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    "message": "Success",
                    "data": serializer.data,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Update an existing Color Checking Report",
        operation_description="This PUT API request updates an existing color checking report.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                description='Bearer token (format: Bearer <Token>)',
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        request_body=ColorcheckingreportSerializer,
        responses={
            200: openapi.Response(description="Updated"),
            400: openapi.Response(description="Bad Request"),
            404: openapi.Response(description="Not Found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Color Checking Report']
    )
    def put(self, request, pk):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            report = Colorcheckingreport.objects.get(pk=pk)
            request.data['mdatetime'] = datetime.now(timezone.utc)
            serializer = ColorcheckingreportSerializer(report, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    "message": "Success",
                    "data": serializer.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Colorcheckingreport.DoesNotExist:
            return Response({'error': 'Colorcheckingreport not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Delete a Color Checking Report",
        operation_description="This DELETE API request deletes an existing color checking report.",
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
            200: openapi.Response(description="Deleted"),
            404: openapi.Response(description="Not Found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Color Checking Report']
    )
    def delete(self, request, pk):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            report = Colorcheckingreport.objects.get(pk=pk)
            report.delete()
            response_data = {
                "message": "Success",
                "data": f"Colorcheckingreport with id {pk} deleted successfully",
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Colorcheckingreport.DoesNotExist:
            return Response({'error': 'Colorcheckingreport not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
