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
    Pastingmaster,
    Extracostmaster,
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
    PastingmasterSerializer,
    ExtracostmasterSerializer,
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

    
# Page Load API...
class ProductDetail(APIView):
    """
        This API is used for product specification (FP History Web) Page Load API
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    def post(self, request):
        # DropDownView instance from generalapis app,
        dropdown_view = DropDownView()
        dropdown_response = dropdown_view.post(request)
        drp = {}

        if dropdown_response.status_code == status.HTTP_200_OK:

            dropdown_data = dropdown_response.data
            dropdown_data.update({
                'JobType': get_general_dropdown('JobType'),
                'NewRepeat': get_general_dropdown('NewRepeat')
            })
            
            return Response(dropdown_data, status=status.HTTP_200_OK)
        else:
            return Response(dropdown_response.data, status=dropdown_response.status_code)


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

class PaperBoard(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

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
        
        try:
            windowpatching_data = Windowpatchtype.objects.filter(isactive=1)
            windowpatching_serializer = WindowpatchtypeSerializer(windowpatching_data, many=True)
            response_wp['WindowPatchingType'] = windowpatching_serializer.data
                
        except Exception as e:
            response_wp['WindowPatchingType'] = {"error in WindowPatchingType": str(e)}
        
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
    
class FoilingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_fp = {}
        
        # Fetching Foiling Type
        try:
            foiling_data = Foilmaster.objects.all()
            foiling_serializer = FoilTypeSerializer(foiling_data, many=True)
            response_fp['FoilingType'] = foiling_serializer.data
                
        except Exception as e:
            response_fp['FoilingType'] = {"error in FoilingType": str(e)}
        
        # Fetching Foiling Group
        group_string = '00007'
        response_fp['groups'] = get_group_data(group_string)

        # Fetching Machines
        machinelist = get_machine_process_data('FF', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_fp['machines'] = machine_data.data
        response_fp['JobComplexity'] = get_complexity('FF',1)

        return Response(response_fp, status=status.HTTP_200_OK)
    
class EmbossingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_ep = {}
        
        # Fetching Embossing Type
        try:
            embossing_data = ItemEmbosetypeMaster.objects.filter(isactive=1)
            embossing_serializer = ItemEmbosetypeMasterSerializer(embossing_data, many=True)
            response_ep['EmbossingType'] = embossing_serializer.data
                
        except Exception as e:
            response_ep['EmbossingType'] = {"error in EmbossingType": str(e)}
        
        # Fetching Embossing Group
        group_string = '00008'
        response_ep['groups'] = get_group_data(group_string)

        # Fetching Machines
        machinelist = get_machine_process_data('EM', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_ep['machines'] = machine_data.data
        response_ep['JobComplexity'] = get_complexity('EM',1)

        return Response(response_ep, status=status.HTTP_200_OK)
    
class PunchingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_pp = {}
        
        # Fetching Machine
        machinelist = get_machine_process_data('SC', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_pp['machines'] = machine_data.data
        response_pp['JobComplexity'] = get_complexity('SC',1)
        return Response(response_pp, status=status.HTTP_200_OK)
    
class FinishCuttingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_fc = {}
        
        # Fetching Machine
        response_fc['JobComplexity'] = get_complexity('FC',1)
        return Response(response_fc, status=status.HTTP_200_OK)

class SealingPastingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_sp = {}
        
        response_sp['Type'] = get_general_dropdown('SealingPastingType')
        response_sp['MachineManual'] = get_general_dropdown('SealingPastingMnM')
        # Fetching Embossing Group
        group_string = '00003'
        response_sp['groups'] = get_group_data(group_string)

        # Pasting type
        try:
            pasting_data = Pastingmaster.objects.filter(inuse=1)
            pasting_serializer = PastingmasterSerializer(pasting_data, many=True)
            response_sp['PastingType'] = pasting_serializer.data
                
        except Exception as e:
            response_sp['PastingType'] = {"error in PastingType": str(e)}

        # Fetching Machine
        machinelist = get_machine_process_data('Pa', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_sp['machines'] = machine_data.data
        response_sp['JobComplexity'] = get_complexity('Pa',1)

        return Response(response_sp, status=status.HTTP_200_OK)

class FoldingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_fp = {}
        
        # Fetching Machine
        machinelist = get_machine_process_data('FF', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_fp['machines'] = machine_data.data
        response_fp['JobComplexity'] = get_complexity('FF',1)

        return Response(response_fp, status=status.HTTP_200_OK)

class CorrugationProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_cp = {}
        
        # Fetching Machine
        machinelist = get_machine_process_data('FM', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_cp['machines'] = machine_data.data
        response_cp['JobComplexity'] = get_complexity('FM',1)

        # Fetch group information
        group_string = '00001,00101,00034,00102'
        response_cp['groups'] = get_group_data(group_string)

        # Fetching Flute Type
        try:
            flute_data = Flutemaster.objects.filter(isactive=1)
            flute_serializer = FlutemasterSerializer(flute_data, many=True)
            response_cp['FluteType'] = flute_serializer.data
                
        except Exception as e:
            response_cp['FluteType'] = {"error in FluteType": str(e)}


        return Response(response_cp, status=status.HTTP_200_OK)

class CorrugationSheetPastingAdhesive(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_cs_pa = {}

        response_cs_pa['CorrSheetPasting'] = get_general_dropdown('CorrSheetPasting')
        response_cs_pa['Kind'] = get_general_dropdown('CorrSheetPastingKind')
        return Response(response_cs_pa, status=status.HTTP_200_OK)
    
class PackingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_pp = {}
        
        # Fetching Machine
        machinelist = get_machine_process_data('PACK', icompanyid)
        machine_data = MachineProcessSerializer(machinelist, many=True)
        response_pp['machines'] = machine_data.data
        # Fetching groups
        group_string = '00154'
        response_pp['groups'] = get_group_data(group_string)
        response_pp['PolyLinning'] = get_general_dropdown('PolyLinning')
        response_pp['Strapping'] = get_general_dropdown('Strapping')
        return Response(response_pp, status=status.HTTP_200_OK)

class otherProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_op = {}
        
        # Fetching OtherProcess ProcessType
        try:
            other_process_data = Extracostmaster.objects.filter(isactive=1)
            other_process_serializer = ExtracostmasterSerializer(other_process_data, many=True)
            response_op['Process'] = other_process_serializer.data
                
        except Exception as e:
            response_op['Process'] = {"error in other process Type": str(e)}

        response_op['groups'] = "Group dont know talk to ritesh sir"
        return Response(response_op, status=status.HTTP_200_OK)

class SortingProcess(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_sp = {}
        
        # Fetching Machine 
        response_sp['Process'] = get_general_dropdown('SortingProcess')
        return Response(response_sp, status=status.HTTP_200_OK)
    
class SheetChecking(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    def get(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        response_sc = {}
        
        response_sc['Process'] = get_general_dropdown('SheetCheckProcess')
        return Response(response_sc, status=status.HTTP_200_OK)


class OurSpecification(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Retrival of all required data of our specification tab ( Page Load API) ",
        operation_description="In this Get API request we are sending all page load data related to page load",
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

        # Foiling Process data..
        class_foiling = FoilingProcess()
        response_foiling = class_foiling.get(request)
        foiling_data = response_foiling.data

        # Embossing Process data..
        class_embossing = EmbossingProcess()
        response_embossing = class_embossing.get(request)
        embossing_data = response_embossing.data

        # Punching Process data..
        class_punching = PunchingProcess()
        response_punching = class_punching.get(request)
        punching_data = response_punching.data

        # Finish Cutting Process data..
        class_finish_cutting = FinishCuttingProcess()
        response_finish_cutting = class_finish_cutting.get(request)
        finish_cutting_data = response_finish_cutting.data

        # Sealing Pasting Process data..
        class_sealing_pasting = SealingPastingProcess()
        response_sealing_pasting = class_sealing_pasting.get(request)
        sealing_pasting_data = response_sealing_pasting.data

        # Folding Process data..
        class_folding = FoldingProcess()
        response_folding = class_folding.get(request)
        folding_data = response_folding.data

        # Corrugation Process data..
        class_corrugation = CorrugationProcess()
        response_corrugation = class_corrugation.get(request)
        corrugation_data = response_corrugation.data

        # Corrugation Sheet Pasting Process data..
        class_corrugation_sheet_pasting = CorrugationSheetPastingAdhesive()
        response_corrugation_sheet_pasting = class_corrugation_sheet_pasting.get(request)
        corrugation_sheet_pasting_data = response_corrugation_sheet_pasting.data

        # Packing Process data..
        class_packing = PackingProcess()
        response_packing = class_packing.get(request)
        packing_data = response_packing.data

        # Other Process data..
        class_other_process = otherProcess()
        response_other_process = class_other_process.get(request)
        other_process_data = response_other_process.data
        
        # Sorting Process data..
        class_sorting_process = SortingProcess()
        response_sorting_process = class_sorting_process.get(request)
        sorting_process_data = response_sorting_process.data

        # Sheet Checking Process data..
        class_sheet_checking = SheetChecking()
        response_sheet_checking = class_sheet_checking.get(request)
        sheet_checking_data = response_sheet_checking.data



        response_data = {
            "PaperBoard": paper_board_data,
            "Printing": printing_data,
            "Coating": coating_data,
            "Lamination": lamination_data,
            "MetPetLamination": metpet_lamination_data,
            "WindowPatching": window_patching_data,
            "Foiling": foiling_data,
            "Embossing": embossing_data,
            "Punching": punching_data,
            "FinishCutting": finish_cutting_data,
            "SealingPasting": sealing_pasting_data,
            "Folding": folding_data,
            "Corrugation": corrugation_data,
            "CorrugationSheetPasting": corrugation_sheet_pasting_data,
            "Packing":packing_data,
            "OtherProcess":other_process_data,
            "Sorting": sorting_process_data,
            "SheetChecking": sheet_checking_data,
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
        operation_summary="Raw material API for our specifications tab",
        operation_description="This API call frequently as per requirement",
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