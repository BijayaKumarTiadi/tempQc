# views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mastersapp.models import Companymaster, Employeemaster, ItemClass, ItemFpmasterext, ItemUnitMaster, ProductCategoryMaster
from .serializers import CompanySerializer, EmployeeSerializer, ItemClassSerializer, ItemFpmasterQualitySerializer, UnitMasterSerializer, ProductCategorySerializer
from accounts.helpers import GetUserData
from django.core.exceptions import ObjectDoesNotExist

class DropDownView(APIView):
    """
    API view for fetching dropdown values for various master models
    """

    def post(self, request):
        # user = GetUserData.get_user(request)
        # icompanyid = user.icompanyid

        # if icompanyid is None:
        #     return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)

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

                isactive = employeemaster_data.get('IsActive', 1) # default when key not present
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

                isactive = productclass_data.get('IsActive', 1) # default when key not present
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
                isactive = productkind_data.get('IsActive', 1) # default when key not present

                productkind_filter = {}
                if isactive == 0:
                    productkind_filter['isactive'] = 0
                elif isactive == 1:
                    productkind_filter['isactive'] = 1

                # productkinds = ItemFpmasterext.objects.filter(**productkind_filter).order_by('quality').distinct('quality')
                productkinds = ItemFpmasterext.objects.filter(**productkind_filter).values('quality').distinct().order_by('quality')
                productkinds_results = ItemFpmasterQualitySerializer(productkinds, many=True).data
                response_data["data"]['ProductKindList'] = productkinds_results

            if 'ProductCategory' in data:
                productcategory_data = data['ProductCategory']
                productcategory_filter = {}
                isactive = productcategory_data.get('IsActive', 1) # default when key not present
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
                isactive = unitmaster_data.get('IsActive', 1) # default when key not present
                if isactive == 0:
                    unitmaster_filter['isactive'] = 0
                elif isactive == 1:
                    unitmaster_filter['isactive'] = 1
                
                units = ItemUnitMaster.objects.filter(**unitmaster_filter).order_by('unitname')
                units_results = UnitMasterSerializer(units, many=True).data
                response_data["data"]['UnitMasterList'] = units_results

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'No records found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
