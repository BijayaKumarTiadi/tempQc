# views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mastersapp.models import (
    Companymaster,
    Employeemaster,
    ItemClass,
    ItemFpmasterext,
    ItemUnitMaster,
    ProductCategoryMaster,
)
from generalapis.serializers import (
    CompanySerializer,
    EmployeeSerializer,
    ItemClassSerializer,
    ItemFpmasterQualitySerializer,
    UnitMasterSerializer,
    ProductCategorySerializer,
)
from .models import (
    EstJobcomplexity,
    CoatingMaster,
    Lammaster,
    Windowpatchtype,
    Foilmaster,
    ItemEmbosetypeMaster,
    Flutemaster,
    ItemMachinenames,
    ItemProcessname,
)

from .serializers import (
    JobComplexitySerializer,
    CoatingMasterSerializer,
    LammasterSerializer,
    WindowpatchtypeSerializer,
    FoilTypeSerializer,
    ItemEmbosetypeMasterSerializer,
    FlutemasterSerializer,
    MachineProcessSerializer,
)


#
from generalapis.views import DropDownView
from django.core.exceptions import ObjectDoesNotExist

# Installed Library imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import os
import json
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import connection, connections, DatabaseError
from django.db import transaction
from rest_framework import serializers

# Custom imports
from .permissions import ViewByStaffOnlyPermission
from accounts.helpers import GetUserData
from django.db.models import F


PRID_MAPPING = {
    'paperBoardMachine': 'PCut',
    'printingMachine': 'Pr',
    'coatingMachine': 'FC',
    'LamAndMetMachine': 'FL',
    'windowMachine': 'WP',
    'foldingFoilingMachine': 'FF',
    'embossingMachine': 'EM',
    'punchingSheetChkMachine': 'SC',
    'sealPastMachine': 'Pa',
    'corrMachineE': 'FM',
    'CorrSheetPastMachineB': 'FP',
    'packingMachine': 'PACK',
    'otherProcessMachine': 'otherProcessMachine'
}

class MachineList(APIView):
    """
    This API is used in Product Specification Process,
    Api is Process wise,
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Retrieve machine list based on process.",
        operation_description="response providing as per PRID_MAPPING list of processes",
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
        responses={
            200: "Success",
            401: "Unauthorized",
            500: "Internal server error"
        },
        tags=['Product Specification (FP History Web)']
    )
    

    def get(self, request, *args, **kwargs):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {}

        try:
            with connection.cursor() as cursor:
                for machine_process_name, prid in PRID_MAPPING.items():
                    cursor.execute("""
                        SELECT 
                            a.MachineID, a.RecID, a.MachineName, b.PrID, b.PrName, b.Description 
                        FROM 
                            item_machinenames a 
                        JOIN 
                            item_processname b 
                        ON 
                            a.BasePrUniqueID = b.BasePrUniqueID 
                        WHERE 
                            b.PrID=%s AND a.InUse='1' AND a.icompanyid=%s
                        """, [prid, '00001'])
                    rows = cursor.fetchall()

                    if rows:
                        response_data[machine_process_name] = [
                            {
                                'machineid': row[0],
                                'recid': row[1],
                                'machinename': row[2],
                                'prid': row[3],
                                'prname': row[4],
                                'description': row[5]
                            } for row in rows
                        ]
                    else:
                        response_data[machine_process_name] = []

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


class PageLoadAPI(APIView):
    """
        This API is used for product specification (FP History Web) Page Load API
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="ProductSpecification Page Load API",
        operation_description="API is working as per front end post request",
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
                'clientmaster': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'companyid': openapi.Schema(type=openapi.TYPE_STRING, description="Company ID"),
                        'CompanyNameLike': openapi.Schema(type=openapi.TYPE_STRING, description="Company name partial match"),
                        'isactive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['companyid', 'isactive']
                ),
                'EmployeeMaster': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'Dept': openapi.Schema(type=openapi.TYPE_STRING, description="Department name"),
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['Dept', 'IsActive']
                ),
                'ProductClass': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['IsActive']
                ),
                'ProductKind': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['IsActive']
                ),
                'ProductCategory': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['IsActive']
                ),
                'UnitMaster': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['IsActive']
                ),
                'GroupMaster': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'groupid': openapi.Schema(type=openapi.TYPE_STRING, description="Group ID filteration if required"),
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                ),
                'CoatingMaster': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['IsActive']
                ),
                'WindowPatchingType': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['IsActive']
                ),
                'EmbossType': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['IsActive']
                ),
                'FluteType': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
                    },
                    required=['IsActive']
                ),
            },
            required=[],
            example={
                "clientmaster": {
                    "companyid": "00102",
                    "CompanyNameLike": "",
                    "isactive": 1
                },
                "EmployeeMaster": {
                    "Dept": "Marketing",
                    "IsActive": 0
                },
                "ProductClass": {
                    "IsActive": 2
                },
                "ProductKind": {
                    "IsActive": 1
                },
                "ProductCategory": {
                    "IsActive": 1
                },
                "UnitMaster": {
                    "IsActive": 1
                },
                "GroupMaster": {
                    "groupid": "",
                    "IsActive": 1
                },
                "CoatingMaster": {
                    "IsActive": 1
                },
                "WindowPatchingType": {
                    "IsActive": 1
                },
                "EmbossType": {
                    "IsActive": 1
                },
                "FluteType": {
                    "IsActive": 1
                }
            }
        ),
        responses={
            200: "Request was successful",
            400: "Invalid request",
            500: "Internal server error"
        },
        tags=['Product Specification (FP History Web)']
    )

    def post(self, request):
        # DropDownView instance from generalapis app,
        dropdown_view = DropDownView()
        dropdown_response = dropdown_view.post(request)

        if dropdown_response.status_code == status.HTTP_200_OK:
            dropdown_data = dropdown_response.data


            # # Fetching Machine List data
            # try:
            #     machine_list_view = MachineList()
            #     machine_list_response = machine_list_view.get(request)
                
            #     if machine_list_response.status_code == status.HTTP_200_OK:
            #         machine_list_data = machine_list_response.data
            #         dropdown_data.update(machine_list_data)
            #     else:
            #         return Response({"error in MachineList": machine_list_response.data}, status=machine_list_response.status_code)

            # except Exception as e:
            #     return Response({"error in MachineList": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Fetching job complexity data
            try:
                job_complexity_data = EstJobcomplexity.objects.all()
                job_complexity_serializer = JobComplexitySerializer(job_complexity_data, many=True)
                dropdown_data['JobComplexity'] = job_complexity_serializer.data
            except Exception as e:
                return Response({"error in Job Complexity": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Fetching PTurnType data using raw SQL query
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT ID, PTurnType, IsActive FROM FP_PTURNTYPE WHERE IsActive='1' ORDER BY PTurnType DESC;")
                    pturntype_data = cursor.fetchall()

                    # Adding raw data to the response
                    dropdown_data['PTurnType'] = [
                        {'ID': row[0], 'PTurnType': row[1], 'IsActive': row[2]} for row in pturntype_data
                    ]
            except Exception as e:
                return Response({"error in PTurnType": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Fetching CoatingMaster data
            try:
                data = request.data
                if 'CoatingMaster' in data:
                    coatingmaster_data = data['CoatingMaster']
                    coating_filter = {}
                    isactive = coatingmaster_data.get('IsActive', None)
                    if isactive in [0, 1]:
                        coating_filter['isactive'] = isactive
                    coating_data = CoatingMaster.objects.filter(**coating_filter)
                    coating_serializer = CoatingMasterSerializer(coating_data, many=True)
                    dropdown_data['CoatingMaster'] = coating_serializer.data
                
            except Exception as e:
                return Response({"error in CoatingMaster": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Fetching Lamination Type
            try:
                lamination_data = Lammaster.objects.all()
                lamination_serializer = LammasterSerializer(lamination_data, many=True)
                dropdown_data['LaminationType'] = lamination_serializer.data
                
            except Exception as e:
                return Response({"error in LaminationType": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Fetching Window Patching Type
            try:
                if 'WindowPatchingType' in data:
                    windowpatching_data = data['WindowPatchingType']
                    windowpatching_filter = {}
                    isactive = windowpatching_data.get('IsActive', None)
                    if isactive in [0, 1]:
                        windowpatching_filter['isactive'] = isactive
                    windowpatching_data = Windowpatchtype.objects.filter(**windowpatching_filter)
                    windowpatching_serializer = WindowpatchtypeSerializer(windowpatching_data, many=True)
                    dropdown_data['WindowPatchingType'] = windowpatching_serializer.data
                
            except Exception as e:
                return Response({"error in WindowPatchingType": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Fetching Foil Type,
            try:
                foil_data = Foilmaster.objects.all()
                foil_serializer = FoilTypeSerializer(foil_data, many=True)
                dropdown_data['FoilType'] = foil_serializer.data
                
            except Exception as e:
                return Response({"error in FoilType": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Fetching Embose Type,
            try:
                data = request.data
                if 'EmbossType' in data:
                    emboss_data = data['EmbossType']
                    emboss_filter = {}
                    isactive = emboss_data.get('IsActive', None)
                    if isactive in [0, 1]:
                        emboss_filter['isactive'] = isactive
                    emboss_data = ItemEmbosetypeMaster.objects.filter(**emboss_filter)
                    emboss_serializer = ItemEmbosetypeMasterSerializer(emboss_data, many=True)
                    dropdown_data['EmbossType'] = emboss_serializer.data
                
            except Exception as e:
                return Response({"error in EmbossType": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Fetching Flute Type,
            try:
                data = request.data
                if 'FluteType' in data:
                    flute_data = data['FluteType']
                    flute_filter = {}
                    isactive = flute_data.get('IsActive', None)
                    if isactive in [0, 1]:
                        flute_filter['isactive'] = isactive
                    flute_data = Flutemaster.objects.filter(**flute_filter)
                    flute_serializer = FlutemasterSerializer(flute_data, many=True)
                    dropdown_data['FluteType'] = flute_serializer.data
                
            except Exception as e:
                return Response({"error in FluteType": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

            return Response(dropdown_data, status=status.HTTP_200_OK)
        else:
            return Response(dropdown_response.data, status=dropdown_response.status_code)
