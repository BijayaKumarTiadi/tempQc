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
    ItemGroupMaster,
)
from .serializers import (
    CompanySerializer,
    EmployeeSerializer,
    ItemClassSerializer,
    ItemFpmasterQualitySerializer,
    UnitMasterSerializer,
    ProductCategorySerializer,
    ItemGroupSerializer,
)
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


class DropDownView(APIView):
    """
    API view for fetching dropdown values for various master models
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Master API List",
        operation_description="Required Master List Provided as per front end request.",
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
                        'isactive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive)")
                    },
                    required=['companyid', 'isactive']
                ),
                'EmployeeMaster': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'Dept': openapi.Schema(type=openapi.TYPE_STRING, description="Department name"),
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive)")
                    },
                    required=['Dept', 'IsActive']
                ),
                'ProductClass': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive)")
                    },
                    required=['IsActive']
                ),
                'ProductKind': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive)")
                    },
                    required=['IsActive']
                ),
                'ProductCategory': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive)")
                    },
                    required=['IsActive']
                ),
                'UnitMaster': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive)")
                    },
                    required=['IsActive']
                ),
                'GroupMaster': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'GroupID': openapi.Schema(type=openapi.TYPE_STRING, description="Group ID filteration if required"),
                        'IsActive': openapi.Schema(type=openapi.TYPE_INTEGER, description="Active status (1 for active, 0 for inactive)")
                    },
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
                    "GroupID": "",
                    "IsActive": 1
                }
                
            }
        ),
        responses={
            200: "Request was successful",
            400: "Invalid request",
            500: "Internal server error"
        },
        tags=['General API']
    )
    def post(self, request):
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = request.data
            response_data = {"message": "Success", "data": {}}

            # Apply filters for Companymaster if clientmaster key exists
            if 'clientmaster' in data:
                clientmaster_data = data['clientmaster']
                company_filter = {}

                # Check if 'companyid' exists and is not empty within 'clientmaster'
                if 'companyid' in clientmaster_data and clientmaster_data['companyid']:
                    company_filter['companyid'] = clientmaster_data['companyid']

                if 'CompanyNameLike' in clientmaster_data and clientmaster_data['CompanyNameLike']:
                    company_filter['companyname__icontains'] = clientmaster_data['CompanyNameLike']

                isactive = clientmaster_data.get('isactive', 1)
                if isactive == 0:
                    company_filter['isactive'] = 0
                elif isactive == 1:
                    company_filter['isactive'] = 1

                companies = Companymaster.objects.filter(**company_filter).order_by('companyname')
                companies_results = CompanySerializer(companies, many=True).data
                response_data["data"]['ClientList'] = companies_results

            # Apply filters for Employeemaster if EmployeeMaster key exists
            if 'EmployeeMaster' in data:
                employeemaster_data = data['EmployeeMaster']
                employee_filter = {}

                if 'Dept' in employeemaster_data and employeemaster_data['Dept']:
                    employee_filter['dept'] = employeemaster_data['Dept']

                isactive = employeemaster_data.get('IsActive', 1)  # default when key not present
                if isactive == 0:
                    employee_filter['isactive'] = 0
                elif isactive == 1:
                    employee_filter['isactive'] = 1

                employees = Employeemaster.objects.filter(**employee_filter).order_by('empname')
                employees_results = EmployeeSerializer(employees, many=True).data
                response_data["data"]['MarExeList'] = employees_results

            # Apply filters for ItemClass if ProductClass key exists
            if 'ProductClass' in data:
                productclass_data = data['ProductClass']
                itemclass_filter = {}

                isactive = productclass_data.get('IsActive', 1)  # default when key not present
                if isactive == 0:
                    itemclass_filter['isactive'] = 0
                elif isactive == 1:
                    itemclass_filter['isactive'] = 1

                itemclasses = ItemClass.objects.filter(**itemclass_filter).order_by('classname')
                itemclasses_results = ItemClassSerializer(itemclasses, many=True).data
                response_data["data"]['ProductClassList'] = itemclasses_results

            # Apply filters for ItemFpmasterext if ProductKind key exists
            if 'ProductKind' in data:
                productkind_data = data['ProductKind']
                isactive = productkind_data.get('IsActive', 1)  # default when key not present

                productkind_filter = {}
                if isactive == 0:
                    productkind_filter['isactive'] = 0
                elif isactive == 1:
                    productkind_filter['isactive'] = 1

                productkinds = ItemFpmasterext.objects.filter(**productkind_filter).values('quality').distinct().order_by('quality')
                productkinds_results = ItemFpmasterQualitySerializer(productkinds, many=True).data
                response_data["data"]['ProductKindList'] = productkinds_results

            if 'ProductCategory' in data:
                productcategory_data = data['ProductCategory']
                productcategory_filter = {}
                isactive = productcategory_data.get('IsActive', 1)  # default when key not present
                if isactive == 0:
                    productcategory_filter['isactive'] = 0
                elif isactive == 1:
                    productcategory_filter['isactive'] = 1

                productcategories = ProductCategoryMaster.objects.filter(**productcategory_filter).order_by('particular')
                productcategories_results = ProductCategorySerializer(productcategories, many=True).data
                response_data["data"]['ProductCategoryList'] = productcategories_results

            if 'UnitMaster' in data:
                unitmaster_data = data['UnitMaster']
                unitmaster_filter = {}
                isactive = unitmaster_data.get('IsActive', 1)  # default when key not present
                if isactive == 0:
                    unitmaster_filter['isactive'] = 0
                elif isactive == 1:
                    unitmaster_filter['isactive'] = 1

                units = ItemUnitMaster.objects.filter(**unitmaster_filter).order_by('unitname')
                units_results = UnitMasterSerializer(units, many=True).data
                response_data["data"]['UnitMasterList'] = units_results


            if 'GroupMaster' in data:
                groupmaster_data = data['GroupMaster']
                groupmaster_filter = {}
                
                # Check if 'groupid' exists and is not empty within 'GroupMaster'
                if 'GroupID' in groupmaster_data and groupmaster_data['GroupID']:
                    groupmaster_filter['groupid'] = groupmaster_data['GroupID']

                isactive = groupmaster_data.get('IsActive',1) # default when key not present
                if isactive == 0:
                    groupmaster_filter['isactive'] = 0
                elif isactive == 1:
                    groupmaster_filter['isactive'] = 1
                groups = ItemGroupMaster.objects.filter(**groupmaster_filter).order_by('groupname')
                groups_results = ItemGroupSerializer(groups, many=True).data
                response_data["data"]['GroupMasterList'] = groups_results


            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'No records found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
