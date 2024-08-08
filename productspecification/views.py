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
    ItemMaster,
    ItemDimension,
    ItemGroupMaster,
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
    GeneralDropdown,
    Lammetpetmaster,
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
    ItemGroupSerializer,
    GeneralDropdownSerializer,
    LammetpetmasterSerializer,
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
from django.db.models import F, OuterRef, Subquery, FloatField, CharField, IntegerField, Value

# Custom imports
from .permissions import ViewByStaffOnlyPermission
from accounts.helpers import GetUserData
from django.db.models import F


# Machine Data...
def get_machine_process_data(prid, icompanyid):
    with connection.cursor() as cursor:
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
            """, [prid, icompanyid])
        rows = cursor.fetchall()
        
    results = [
        {
            'MachineID': row[0],
            'RecID': row[1],
            'MachineName': row[2],
            'PrID': row[3],
            'PrName': row[4],
            'Description': row[5]
        } 
        for row in rows
    ]

    return results


# Group Data...
def get_group_data(group_ids):
    # If the input is a single ID (not a comma-separated string), treat it as a list with one element
    if isinstance(group_ids, str) and ',' not in group_ids:
        group_id_list = [group_ids]
    else:
        # Split the comma-separated string into a list of group IDs or use it directly if it's already a list
        group_id_list = group_ids.split(',') if isinstance(group_ids, str) else group_ids
    
    # Retrieve group data for each group ID
    item_groups = ItemGroupMaster.objects.filter(groupid__in=group_id_list, isactive=1)
    serializer = ItemGroupSerializer(item_groups, many=True)
    return serializer.data

# Job Complexity...
def get_complexity(pr_id,Active):
    try:
        job_complexity_data = EstJobcomplexity.objects.filter(prid=pr_id,isactive=Active)
        job_complexity_serializer = JobComplexitySerializer(job_complexity_data, many=True)
        return  job_complexity_serializer.data
    except Exception as e:
        return {"error in Job Complexity": str(e)}
    
# General Dropdown...
def get_general_dropdown(dropdown_name):
    try:
        dropdown_data = GeneralDropdown.objects.filter(dropdownname=dropdown_name, isactive=1)
        dropdown_serializer = GeneralDropdownSerializer(dropdown_data, many=True)
        # print(dropdown_serializer.data)
        return dropdown_serializer.data
    except Exception as e:
        return {"error in General Dropdown": str(e)}
    
# Page Load API...
    
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
                # "CoatingMaster": {
                #     "IsActive": 1
                # },
                # "WindowPatchingType": {
                #     "IsActive": 1
                # },
                # "EmbossType": {
                #     "IsActive": 1
                # },
                # "FluteType": {
                #     "IsActive": 1
                # }
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
            
            
            """ Oue Specification Code Merger"""

            # PaperBoard Process Data..
            class_pbp = PaperBoard()
            resp_pbp = class_pbp.get(request)
            paper_board_data = resp_pbp.data

            # Printing Process data..
            class_printing = PrintingProcess()
            response_printing = class_printing.get(request)
            printing_data = response_printing.data

            # Coating Process data..
            class_coating = CoatingProcess()
            response_coating = class_coating.get(request)
            coating_data = response_coating.data

            # Lamination Process data..
            class_lamination = LaminationProcess()
            response_lamination = class_lamination.get(request)
            lamination_data = response_lamination.data

            # MetPet Lamination data..
            class_metpet_lamination = MetPetLaminationProcess()
            response_metpet_lamination = class_metpet_lamination.get(request)
            metpet_lamination_data = response_metpet_lamination.data

            # Window Patching Process data..
            class_window_patching = WindowPatchingProcess()
            response_window_patching = class_window_patching.get(request)
            window_patching_data = response_window_patching.data

            response_data = {
                "ProductDetails": dropdown_response.data,
                "PaperBoard": paper_board_data,
                "Printing": printing_data,
                "Coating": coating_data,
                "Lamination": lamination_data,
                "MetPetLamination": metpet_lamination_data,
                "WindowPatching": window_patching_data,
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(dropdown_response.data, status=dropdown_response.status_code)


class PaperBoard(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Retrieve all process required data",
        operation_description="response in resting Mode",
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

    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_pbp = {}

        machinelist = get_machine_process_data('PCut', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)

        response_pbp['machines'] = machine_data.data

        group_string = '00001,00101,00005,00102'
        response_pbp['groups'] = get_group_data(group_string)

        return Response(response_pbp, status=status.HTTP_200_OK)
    
class PrintingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Retrieve printing process required data",
        operation_description="response in testing Mode",
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
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_pp = {}
        machinelist = get_machine_process_data('Pr', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_pp['machines'] = machine_data.data
        response_pp['JobComplexity'] = get_complexity('Pr',1)
        
        # Fetching PTurnType data using raw SQL query
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT ID, PTurnType, IsActive FROM FP_PTURNTYPE WHERE IsActive='1' ORDER BY PTurnType DESC;")
                pturntype_data = cursor.fetchall()

                # Adding raw data to the response
                response_pp['PTurnType'] = [
                    {'ID': row[0], 'PTurnType': row[1], 'IsActive': row[2]} for row in pturntype_data
                ]
        except Exception as e:
            # return Response({"error in PTurnType": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            response_pp['PTurnType'] = {"error in PTurnType": str(e)}

        response_pp['PrintingType'] = get_general_dropdown('PrintingType')
        response_pp['FrontBack'] = get_general_dropdown('FrontBack')
        group_string = '00002,00109'
        response_pp['groups'] = get_group_data(group_string)

        return Response(response_pp, status=status.HTTP_200_OK)
    
class CoatingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_cp = {}

        # Fetching CoatingMaster data
        try:
            coating_filter = {'isactive__in': [0, 1]}
            coating_data = CoatingMaster.objects.filter(**coating_filter)
            coating_serializer = CoatingMasterSerializer(coating_data, many=True)
            response_cp['CoatingType'] = coating_serializer.data

        except Exception as e:
            response_cp['CoatingType'] = {"error in CoatingMaster(Coating Type)": str(e)}

        group_string = '00156'
        response_cp['groups'] = get_group_data(group_string)

        # Coating Machines
        machinelist = get_machine_process_data('FC', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_cp['machines'] = machine_data.data

        response_cp['Kind'] = get_general_dropdown('CoatingKind')
        response_cp['FrontBack'] = get_general_dropdown('CoatingFrontBack')
        response_cp['JobComplexity'] = get_complexity('FC',1)

        return Response(response_cp, status=status.HTTP_200_OK)

class LaminationProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_lp = {}

        # Fetching Lamination Type
        try:
            lamination_data = Lammaster.objects.all()
            lamination_serializer = LammasterSerializer(lamination_data, many=True)
            response_lp['LaminationType'] = lamination_serializer.data

        except Exception as e:
            response_lp['LaminationType'] = {"error in LaminationType": str(e)}

        group_string = '00006,00003'
        response_lp['groups'] = get_group_data(group_string)
        response_lp['TypeOfLamination'] = get_general_dropdown('LaminationType')
        response_lp['FrontBack'] = get_general_dropdown('LaminationFrontBack')

        # Lamination machines
        machinelist = get_machine_process_data('FL', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_lp['machines'] = machine_data.data
        response_lp['JobComplexity'] = get_complexity('FL',1)

        return Response(response_lp, status=status.HTTP_200_OK)
    
class MetPetLaminationProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_mplp = {}
        # Fetching Metal Pet Lamination Type
        try:
            metpet_lamination_data = Lammetpetmaster.objects.all()
            metpet_lamination_serializer = LammetpetmasterSerializer(metpet_lamination_data, many=True)

            response_mplp['MetPetLaminationType'] = metpet_lamination_serializer.data
        except Exception as e:
            response_mplp['MetPetLaminationType'] = {"error in MetPetLaminationType": str(e)}

        # Lamination machines
        machinelist = get_machine_process_data('FL', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_mplp['machines'] = machine_data.data
        group_string = '00006,00003'
        response_mplp['groups'] = get_group_data(group_string)
        response_mplp['Kind'] = get_general_dropdown('MetPetKind')
        response_mplp['FrontBack'] = get_general_dropdown('LaminationFrontBack')
        response_mplp['JobComplexity'] = get_complexity('FL',1)
        
        return Response(response_mplp, status=status.HTTP_200_OK)
    
class WindowPatchingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_wp = {}
        
        # Fetching Window Patching Type
        """
        try:
            data = request.data
            if 'WindowPatchingType' in data:
                windowpatching_data = data['WindowPatchingType']
                windowpatching_filter = {}
                isactive = windowpatching_data.get('IsActive', None)
                if isactive in [0, 1]:
                    windowpatching_filter['isactive'] = isactive
                windowpatching_data = Windowpatchtype.objects.filter(**windowpatching_filter)
                windowpatching_serializer = WindowpatchtypeSerializer(windowpatching_data, many=True)
                response_wp['WindowPatchingType'] = windowpatching_serializer.data
                
        except Exception as e:
            response_wp['WindowPatchingType'] = {"error in WindowPatchingType": str(e)}
        """
        # Fetching Window Patching Group
        group_string = '00051,00003'
        response_wp['groups'] = get_group_data(group_string)

        # Fetching Window Patching Machine
        machinelist = get_machine_process_data('WP', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_wp['machines'] = machine_data.data
        response_wp['Unit'] = get_general_dropdown('WPUnit')
        response_wp['JobComplexity'] = get_complexity('WP',1)

        return Response(response_wp, status=status.HTTP_200_OK)
    
class ProcessAllData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Retrieve all process required data",
        operation_description="response in resting Mode",
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

    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # PaperBoard Process Data..
        class_pbp = PaperBoard()
        resp_pbp = class_pbp.get(request)
        paper_board_data = resp_pbp.data

        # Printing Process data..
        class_printing = PrintingProcess()
        response_printing = class_printing.get(request)
        printing_data = response_printing.data

        # Coating Process data..
        class_coating = CoatingProcess()
        response_coating = class_coating.get(request)
        coating_data = response_coating.data

        # Lamination Process data..
        class_lamination = LaminationProcess()
        response_lamination = class_lamination.get(request)
        lamination_data = response_lamination.data

        # MetPet Lamination data..
        class_metpet_lamination = MetPetLaminationProcess()
        response_metpet_lamination = class_metpet_lamination.get(request)
        metpet_lamination_data = response_metpet_lamination.data

        # Window Patching Process data..
        class_window_patching = WindowPatchingProcess()
        response_window_patching = class_window_patching.get(request)
        window_patching_data = response_window_patching.data

        response_data = {
            "PaperBoard": paper_board_data,
            "Printing": printing_data,
            "Coating": coating_data,
            "Lamination": lamination_data,
            "MetPetLamination": metpet_lamination_data,
            "WindowPatching": window_patching_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


# Get Raw Material For Our Specifications tab.
class GetRawMaterial(APIView):
    """
    This API Class provides raw material data for product specifications form.
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
                'GroupID': openapi.Schema(type=openapi.TYPE_STRING, description="Group ID"),
                'ValueLike': openapi.Schema(type=openapi.TYPE_STRING, description="Item name partial match"),
                'isactive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive, 2 for all)")
            },
            required=['GroupID', 'ValueLike', 'isactive'],
            example={
                "GroupID": "00001",
                "ValueLike": "Pearl",
                "isactive": 1
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
        user = GetUserData.get_user(request)
        PIcompanyID = user.icompanyid

        PGroupID = request.data.get('GroupID')
        PValueLike = request.data.get('ValueLike', '')
        isactive = request.data.get('isactive', 1)

        if not PGroupID or not PIcompanyID:
            return Response({"error": "GroupID and ValueLike are required"}, status=status.HTTP_400_BAD_REQUEST)

        PKind = PValueLike.replace(' ', '')

        try:
            items = []

            filter_conditions = {
                'groupid': PGroupID,
                'description__icontains': PKind
            }

            if isactive != 2:
                filter_conditions['isactive'] = isactive

            subquery_length = Subquery(
                ItemDimension.objects.filter(itemid=OuterRef('itemid')).values('length')[:1],
                output_field=FloatField()
            )
            subquery_breadth = Subquery(
                ItemDimension.objects.filter(itemid=OuterRef('itemid')).values('breadth')[:1],
                output_field=FloatField()
            )
            subquery_thickness = Subquery(
                ItemDimension.objects.filter(itemid=OuterRef('itemid')).values('thickness')[:1],
                output_field=FloatField()
            )

            if PGroupID == '00001':  # Board
                items = ItemMaster.objects.filter(
                    **filter_conditions,
                    itemid__in=ItemDimension.objects.values_list('itemid', flat=True)
                ).annotate(
                    Deckle=subquery_length / 10,
                    Grain=subquery_breadth / 10,
                    gsm=subquery_thickness
                ).values(
                    'itemid', 'description', 'iprefix', 'quality', 'manufacturer', 'groupid', 'Deckle', 'Grain', 'gsm'
                )

            elif PGroupID in ('00101', '00005', '00102'):  # paperroll, board roll
                items = ItemMaster.objects.filter(
                    **filter_conditions,
                    groupid__in=['00005', '00101'],
                    itemid__in=ItemDimension.objects.values_list('itemid', flat=True)
                ).annotate(
                    Deckle=subquery_length / 10,
                    gsm=0
                ).values(
                    'itemid', 'description', 'iprefix', 'quality', 'manufacturer', 'groupid', 'Deckle', 'gsm'
                )

            else:
                items = ItemMaster.objects.filter(
                    **filter_conditions
                ).values(
                    'itemid', 'description', 'iprefix', 'groupid'
                )

            results = list(items)

            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)