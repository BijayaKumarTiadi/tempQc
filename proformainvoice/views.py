## Work order Imports
#--Default imports
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import connection, connections, DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers
from django.http import HttpResponse

#--custome imports
from .permissions import ViewByStaffOnlyPermission
from accounts.helpers import GetUserData
from proformainvoice.helper import __gen_pdf__


from mastersapp.models import ItemPiMaster
from proformainvoice.models import ItemPiDetail
from mastersapp.models import Seriesmaster
from mastersapp.models import Companymaster
from mastersapp.models import Employeemaster
from mastersapp.models import CompanymasterEx1
from mastersapp.models import Companydelqtydate
from .models import Paymentterms
from .models import ItemSpec
from .models import Mypref

#-- serializers
from .serializers import ItemPiDetailSerializer, ItemPiMasterSerializer, SeriesSerializer
from .serializers import CompanySerializer
from .serializers import EmployeeSerializer
from .serializers import PaymentTermsSerializer
from .serializers import CompanyEx1Serializer
from .serializers import ItemSpecSerializer
from .serializers import MyprefSerializer
from .serializers import SeriesMasterSaveSerializer
from .serializers import SeriesMasterSaveSerializer, WOMasterSerializer, WODetailSerializer, CompanyDelQtyDateSerializer
from .serializers import ItemWodetailSerializer
from .serializers import ItemWomasterSerializer
from .serializers import ExtendedCompanySerializer


#--Installed Library imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



# Order Management Section 
"""
Informations : ...
"""


class SeriesView(APIView):
    """
    API View to retrieve the list of active series for 'Proforma Invoice' documents for a specific company
    and list of active companies.

    This view requires JWT authentication and specific permissions to be accessed. The series are filtered
    by 'Proforma Invoice' document type, company ID, and their active status. The results are returned in descending
    order by ID.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Get active 'Proforma Invoice' series and active companies  On Page Load Dropdown Lists . ",
        operation_description="Retrieve the list of active series for 'Proforma Invoice' documents for the authenticated user's company and list of all active companies.",
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
            200: openapi.Response(
                description='List of active series and companies',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'seriesresp': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'ID': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the series'),
                                    'Prefix': openapi.Schema(type=openapi.TYPE_STRING, description='Prefix of the series'),
                                    'Isactive': openapi.Schema(type=openapi.TYPE_STRING, description='Active Status of the Series')
                                }
                            )
                        ),
                        'companiesresp': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'CompanyId': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the company'),
                                    'CompanyName': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the company')
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(description='ICompanyID is required'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def get(self, request):
        """
        Handle GET request to retrieve the list of active series for 'Work Order' documents and list of active companies.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A JSON response containing the list of active series and active companies or an error message.
        """
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid
        
        if icompanyid is None:
            return Response({'error': 'ICompanyID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Fetch active 'Work Order' series
            series = Seriesmaster.objects.filter(
                doctype='Proforma Invoice',
                icompanyid=icompanyid,
                # isactive=True
            ).order_by('-id')
            series_results = SeriesSerializer(series, many=True).data
            
            # Fetch active companies
            companies = Companymaster.objects.filter(isactive=True).order_by('companyname')
            companies_results = CompanySerializer(companies, many=True).data

            # Fetch active employees
            # employees = Employeemaster.objects.filter(isactive=True).order_by('empname')
            # employees_results = EmployeeSerializer(employees, many=True).data

            # Fetch active payment terms
            # payment_terms = Paymentterms.objects.filter(isactive=True)
            # payment_terms_results = PaymentTermsSerializer(payment_terms, many=True).data

            # Fetch prefs 
            # mypref_load = Mypref.objects.filter(heading="WorkOrder")
            # mypref_load_results = MyprefSerializer(mypref_load, many=True).data

            # Combine all responses
            response_data = {
                "message": "Success",
                "data": {
                'seriesresp': series_results,
                'companiesresp': companies_results,
                # 'marketingExe': employees_results,
                # 'pay_terms': payment_terms_results,
                # 'prefs': mypref_load_results,
            }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        except ObjectDoesNotExist:
            return Response({'error': 'No records found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientDataView(APIView):
    """
    API View to retrieve contact person details, payment terms, and marketing executive
    based on the client ID provided in the request payload.

    This view requires JWT authentication and specific permissions to be accessed.
    The data is fetched from different models and combined into a single response.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Fetch client-related data at Dropdown On Change ",
        operation_description="Retrieve contact person details, payment terms, and marketing executive based on the client ID.",
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
                'client_id': openapi.Schema(type=openapi.TYPE_STRING, description='Client ID')
            },
            required=['client_id']
        ),
        responses={
            200: openapi.Response(
                description='Client-related data',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'contact_person': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'detailid': openapi.Schema(type=openapi.TYPE_STRING, description='Detail ID'),
                                    'cname': openapi.Schema(type=openapi.TYPE_STRING, description='Contact Name'),
                                    'deptpost': openapi.Schema(type=openapi.TYPE_STRING, description='Department/Post'),
                                    'contactno': openapi.Schema(type=openapi.TYPE_STRING, description='Contact Number'),
                                    'mobileno': openapi.Schema(type=openapi.TYPE_STRING, description='Mobile Number'),
                                    'faxno': openapi.Schema(type=openapi.TYPE_STRING, description='Fax Number'),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                                    'address': openapi.Schema(type=openapi.TYPE_STRING, description='Address'),
                                    'city': openapi.Schema(type=openapi.TYPE_STRING, description='City'),
                                    'state': openapi.Schema(type=openapi.TYPE_STRING, description='State'),
                                }
                            )
                        ),
                        'pay_terms': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'payid': openapi.Schema(type=openapi.TYPE_STRING, description='Payment Term ID'),
                                    'narration': openapi.Schema(type=openapi.TYPE_STRING, description='Narration')
                                }
                            )
                        ),
                        'marketing_executive': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'empid': openapi.Schema(type=openapi.TYPE_STRING, description='Employee ID'),
                                    'empname': openapi.Schema(type=openapi.TYPE_STRING, description='Employee Name')
                                }
                            )
                        ),
                    }
                )
            ),
            400: openapi.Response(description='Client ID is required'),
            404: openapi.Response(description='No company found with the given ID'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        client_id = request.data.get('client_id')
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid # keeping for future reference

        if not client_id:
            return Response({'error': 'Company ID , Client ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch contact person details
            # select empname,empid from companymaster as a,employeemaster as b
            # where a.repid=b.empid and a.companyid='00102'
            # contact_person = CompanymasterEx1.objects.filter(companyid=client_id, isactive=True)
            # contact_person_results = CompanyEx1Serializer(contact_person, many=True).data
            #contact_person
            query = """
                select empname,empid from companymaster as a,employeemaster as b
                where a.repid=b.empid and a.companyid=%s
            """
            # AND ICompanyID = %s add for future reference , fetch by icompany id only .
            with connection.cursor() as cursor:
                cursor.execute(query, [client_id])
                rows = cursor.fetchall()
            contact_person_results = [
                {
                    'empname': row[0],
                    'empid': row[1],
                }
                for row in rows
            ]
            #end contact_person
            #unit_list
            query = """
                select unitid,unitname from item_unit_master  where unitid in('00011','00018','00201')
            """
            # AND ICompanyID = %s add for future reference , fetch by icompany id only .
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            unit_list_results = [
                {
                    'unitid': row[0],
                    'unitname': row[1],
                }
                for row in rows
            ]
            #end unit_list

            # Fetch payterms and marketing executive
            company_details = Companymaster.objects.filter(companyid=client_id, isactive=True).first()
            if not company_details:
                return Response({'error': 'No company found with the given ID'}, status=status.HTTP_404_NOT_FOUND)

            # payterms = Paymentterms.objects.filter(payid=company_details.payid, isactive=True)
            # payterms_results = PaymentTermsSerializer(payterms, many=True).data

            # marketing_executive = Employeemaster.objects.filter(empid=company_details.repid, isactive=True)
            # marketing_executive_results = EmployeeSerializer(marketing_executive, many=True).data

            query = """
                SELECT a.RecordId, a.CompanyName, Get_CompanyNameByRecordId(a.RecordId) as CompanyAddress 
                FROM companydeladdress as a 
                WHERE a.IsActive = 1 AND CompanyID = %s 
                ORDER BY a.CompanyName;
            """
            # AND ICompanyID = %s add for future reference , fetch by icompany id only .
            with connection.cursor() as cursor:
                cursor.execute(query, [client_id])
                rows = cursor.fetchall()

            delivery_address_results = [
                {
                    'RecordId': row[0],
                    'CompanyName': row[1],
                    'CompanyAddress': row[2]
                }
                for row in rows
            ]

            # Combine all responses
            response_data = {
                "message": "Success",
                "data": {
                'contact_person': contact_person_results,
                'unit_list': unit_list_results,
                # 'marketing_executive': marketing_executive_results,
                'delivery_address': delivery_address_results,
            }}
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

'''
class ProductDetailsViewsTry(APIView):
    """
    API View to retrieve product details based on the company ID and additional filters.

    This view requires JWT authentication and specific permissions to be accessed.
    The data is fetched from the ItemFpmasterext and related models, filtered by the provided parameters.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Fetch product details",
        operation_description="Retrieve product details based on the company ID and additional filters.",
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
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category', enum=['1', '2']),
                'clientId': openapi.Schema(type=openapi.TYPE_STRING, description='Client ID'),
                'IPrefix': openapi.Schema(type=openapi.TYPE_STRING, description='IPrefix'),
                'product_desc': openapi.Schema(type=openapi.TYPE_STRING, description='Product Description')
            },
            required=['category', 'clientId']
        ),
        responses={
            200: openapi.Response(
                description='Product details',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'productid': openapi.Schema(type=openapi.TYPE_STRING, description='Product ID'),
                            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Product Name'),
                            'manufacturer': openapi.Schema(type=openapi.TYPE_STRING, description='Manufacturer'),
                            'quality': openapi.Schema(type=openapi.TYPE_STRING, description='Quality'),
                            'rol': openapi.Schema(type=openapi.TYPE_NUMBER, description='Reorder Level'),
                            'unit_name': openapi.Schema(type=openapi.TYPE_STRING, description='Unit Name'),
                            'iprefix': openapi.Schema(type=openapi.TYPE_STRING, description='IPrefix'),
                            'class_name': openapi.Schema(type=openapi.TYPE_STRING, description='Class Name'),
                            'acccode': openapi.Schema(type=openapi.TYPE_STRING, description='Account Code'),
                            'packdetails': openapi.Schema(type=openapi.TYPE_STRING, description='Pack Details')
                        }
                    )
                )
            ),
            400: openapi.Response(description='Company ID, Category, and Client ID are required'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):

        data = json.loads(request.body)
        category = data.get('category')
        clientId = data.get('clientId')
        IPrefix = data.get('IPrefix')
        product_desc = data.get('product_desc')

        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid

        if not icompanyid or not category or not clientId:
            return Response({'error': 'Company ID, Category, and Client ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        filter_conditions = []

        if IPrefix:
            filter_conditions.append(f"a.IPrefix LIKE '%%{IPrefix}%%'")

        if product_desc:
            filter_conditions.append(f"a.Description LIKE '%%{product_desc}%%'")

        if category == '1':  # Client Product
            filter_conditions.append(f"a.Manufacturer = '{clientId}'")

        if category == '2':  # Mother Company Product
            filter_conditions.append(f"h.motherid = '{clientId}'")

        where_clause = ' AND '.join(filter_conditions) if filter_conditions else '1=1'

        query = f"""
            SELECT a.ProductID, REPLACE(a.Description, '\"', '') as ProductName, a.Manufacturer, a.Quality,
                   a.ROL as caseselect, b.UnitName, a.IPrefix, d.classname, a.AccCode, a.PackDetails
            FROM item_fpmasterext AS a
            INNER JOIN item_unit_master AS b ON a.UOM = b.UnitID
            INNER JOIN item_group_master AS c ON a.GroupID = c.GroupID
            INNER JOIN item_class AS d ON a.PackingUnit = d.classid
            INNER JOIN companymaster AS h ON a.Manufacturer = h.companyid
            WHERE a.ICompanyID = %s AND a.IsActive = 1 AND a.GroupID = '00008'
                  AND a.Type = 'F' AND {where_clause}
            GROUP BY a.Description, a.ProductID, a.Manufacturer, a.Quality, b.UnitName
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [icompanyid])
            rows = cursor.fetchall()

            products = [
                {
                    'productid': row[0],
                    'description': row[1],
                    'manufacturer': row[2],
                    'quality': row[3],
                    'rol': row[4],
                    'unit_name': row[5],
                    'iprefix': row[6],
                    'class_name': row[7],
                    'acccode': row[8],
                    'packdetails': row[9]
                }
                for row in rows
            ]

            return Response(products, status=status.HTTP_200_OK)
'''


class ProductDetailsView(APIView):
    """
    API View to retrieve product details based on the company ID and additional filters.

    This view requires JWT authentication and specific permissions to be accessed.
    The data is fetched from the ItemFpmasterext and related models, filtered by the provided parameters.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Fetch finish product lists by FP History Form",
        operation_description="Retrieve product details based on the company ID and additional filters.",
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
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category', enum=['1', '2']),
                'clientId': openapi.Schema(type=openapi.TYPE_STRING, description='Client ID'),
                'IPrefix': openapi.Schema(type=openapi.TYPE_STRING, description='IPrefix'),
                'product_desc': openapi.Schema(type=openapi.TYPE_STRING, description='Product Description')
            },
            required=['category', 'clientId']
        ),
        responses={
            200: openapi.Response(
                description='Product details',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'productid': openapi.Schema(type=openapi.TYPE_STRING, description='Product ID'),
                            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Product Name'),
                            'manufacturer': openapi.Schema(type=openapi.TYPE_STRING, description='Manufacturer'),
                            'quality': openapi.Schema(type=openapi.TYPE_STRING, description='Quality'),
                            'rol': openapi.Schema(type=openapi.TYPE_NUMBER, description='Reorder Level'),
                            'unit_name': openapi.Schema(type=openapi.TYPE_STRING, description='Unit Name'),
                            'iprefix': openapi.Schema(type=openapi.TYPE_STRING, description='IPrefix'),
                            'class_name': openapi.Schema(type=openapi.TYPE_STRING, description='Class Name'),
                            'acccode': openapi.Schema(type=openapi.TYPE_STRING, description='Account Code'),
                            'packdetails': openapi.Schema(type=openapi.TYPE_STRING, description='Pack Details')
                        }
                    )
                )
            ),
            400: openapi.Response(description='Company ID, Category, and Client ID are required'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        data = json.loads(request.body)
        category = data.get('category')
        clientId = data.get('clientId')
        IPrefix = data.get('IPrefix')
        product_desc = data.get('product_desc')

        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid

        if not icompanyid or not category or not clientId:
            return Response({'error': 'Company ID, Category, and Client ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        filter_conditions = self.build_filter_conditions(IPrefix, product_desc, category, clientId)
        query = self.build_query(filter_conditions)

        try:
            products = self.fetch_products(query, icompanyid)
            response_data = {
                "message": "Success",
                "data": {
                    "product_response": products,
                }}
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def build_filter_conditions(self, IPrefix, product_desc, category, clientId):
        """
        Build the filter conditions for the SQL query based on the input parameters.
        """
        filter_conditions = []

        if IPrefix:
            filter_conditions.append(f"a.IPrefix LIKE '%%{IPrefix}%%'")

        if product_desc:
            filter_conditions.append(f"a.Description LIKE '%%{product_desc}%%'")

        if category == '1':  # Client Product
            filter_conditions.append(f"a.Manufacturer = '{clientId}'")

        if category == '2':  # Mother Company Product
            filter_conditions.append(f"h.motherid = '{clientId}'")

        return ' AND '.join(filter_conditions) if filter_conditions else '1=1'

    def build_query(self, filter_conditions):
        """
        Build the SQL query string using the provided filter conditions.
        """
        return f"""
            SELECT a.ProductID, REPLACE(a.Description, '\"', '') as ProductName, a.Manufacturer, a.Quality,
                   a.ROL as caseselect, b.UnitName, a.IPrefix, d.classname, a.AccCode, a.PackDetails
            FROM item_fpmasterext AS a
            INNER JOIN item_unit_master AS b ON a.UOM = b.UnitID
            INNER JOIN item_group_master AS c ON a.GroupID = c.GroupID
            INNER JOIN item_class AS d ON a.PackingUnit = d.classid
            INNER JOIN companymaster AS h ON a.Manufacturer = h.companyid
            WHERE a.ICompanyID = %s AND a.IsActive = 1 AND a.GroupID = '00008'
                  AND a.Type = 'F' AND {filter_conditions}
            GROUP BY a.Description, a.ProductID, a.Manufacturer, a.Quality, b.UnitName
        """

    def fetch_products(self, query, icompanyid):
        """
        Execute the SQL query and fetch the product details.
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [icompanyid])
            rows = cursor.fetchall()

        return [
            {
                'productid': row[0],
                'description': row[1],
                'manufacturer': row[2],
                'quality': row[3],
                'rol': row[4],
                'unit_name': row[5],
                'iprefix': row[6],
                'class_name': row[7],
                'acccode': row[8],
                'packdetails': row[9]
            }
            for row in rows
        ]
    

class EstimatedProductView(APIView):
    """
    View to retrieve estimated products based on various filters.

    This view handles POST requests to filter and retrieve estimated products
    from the database based on the provided category, client ID, IPrefix, and product description.
    - > Not Tested .
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]
    
    @swagger_auto_schema(
        operation_summary="Fetch finish product lists by Estimation Finalization.",
        operation_description="Get estimated products based on filters",
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
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Product category'),
                'clientId': openapi.Schema(type=openapi.TYPE_STRING, description='Client ID'),
                'IPrefix': openapi.Schema(type=openapi.TYPE_STRING, description='IPrefix'),
                'product_desc': openapi.Schema(type=openapi.TYPE_STRING, description='Product description'),
            }
        ),
        responses={200: 'Success', 400: 'Bad Request'},
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        data = json.loads(request.body)
        category = data.get('category')
        clientId = data.get('clientId')
        IPrefix = data.get('IPrefix')
        product_desc = data.get('product_desc')

        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid

        if not icompanyid or not category or not clientId:
            return Response({'error': 'Company ID, Category, and Client ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        filter_conditions = []
        filter2_conditions = []

        if IPrefix:
            filter_conditions.append(f"a.IPrefix LIKE '%%{IPrefix}%%'")
            filter2_conditions.append(f"a.IPrefix LIKE '%%{IPrefix}%%'")

        if product_desc:
            filter_conditions.append(f"a.Description LIKE '%%{product_desc}%%'")
            filter2_conditions.append(f"a.Description LIKE '%%{product_desc}%%'")

        if category == '1':  # Client Product (From Estimation) Category = 1
            filter_conditions.append(f"a.Clientcompid = '{clientId}'")

        if category == '3':  # All Client Product (From Estimation) Category = 3
            # No additional filter for category 3
            pass

        filter_clause = ' AND '.join(filter_conditions) if filter_conditions else '1=1'
        filter2_clause = ' AND '.join(filter2_conditions) if filter2_conditions else '1=1'

        query = f"""
            (SELECT c.Description, CAST(a.Quantity AS DECIMAL) AS Quantity, ROUND(a.finalQrate, 3) AS finalQrate,
                    c.AccCode, c.IPrefix, CONCAT(a.EstimateId, '-', a.RevQuoteNo) AS EstimateId, a.RecordId,
                    b.FPProductID, a.FinalQUnit
             FROM quotationnew AS a
             INNER JOIN quotationnewex2 AS b ON a.recordid = b.recordid
             INNER JOIN item_fpmasterext AS c ON b.FPProductID = c.productid
             WHERE b.FPProductID <> '' AND a.finalqrate > 0 AND a.IcompanyId = %s AND a.IsActive = 1 AND c.IsActive = 1 AND {filter_clause}
             ORDER BY a.QDate DESC)
            UNION
            (SELECT ProductDesc AS Description, '' AS Quantity, FinalRate AS finalQrate, '' AS AccCode, '' AS IPrefix,
                    CONCAT(EstimateID, '-', RevQuoteNo) AS EstimateId, BookID AS RecordId, '' AS FPProductID, QUnit AS FinalQUnit
             FROM BookQuotation
             WHERE ICompanyID = %s AND FinalRate > 0 AND IsActive = 1 AND WOCreated = 0 AND {filter2_clause}
             ORDER BY QDate DESC);
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [icompanyid, icompanyid])
                rows = cursor.fetchall()

                products = [
                    {
                        'description': row[0],
                        'quantity': row[1],
                        'finalQrate': row[2],
                        'acccode': row[3],
                        'iprefix': row[4],
                        'estimateId': row[5],
                        'recordId': row[6],
                        'FPProductID': row[7],
                        'finalQUnit': row[8]
                    }
                    for row in rows
                ]
            response_data = {
                    "message": "Success",
                    "data": {
                        "Estimated_product_response": products,
                    }}
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemSpecView(APIView):
    """
    View to retrieve and save item specifications based on the company ID and item ID.

    This view handles POST requests to filter and retrieve item specifications
    from the database based on the `ICompanyID` of the logged-in user and the `ItemID` provided in the request payload.
    It also handles saving new item specifications.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve and save item specifications",
        operation_description="Retrieve item specifications based on the company ID and item ID. Also allows saving new item specifications.",
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
                'item_id': openapi.Schema(type=openapi.TYPE_STRING, description='Item ID', example='ITEM123'),
                'specid': openapi.Schema(type=openapi.TYPE_STRING, description='Specification ID', example='SPEC001'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description', example='Description of spec'),
                'info1': openapi.Schema(type=openapi.TYPE_STRING, description='Additional info 1', example='Additional info 1'),
                'info2': openapi.Schema(type=openapi.TYPE_STRING, description='Additional info 2', example='Additional info 2')
            },
            required=['item_id']
        ),
        responses={
            200: openapi.Response(
                description='A list of item specifications',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'specid': openapi.Schema(type=openapi.TYPE_STRING, description='Specification ID'),
                            'itemid': openapi.Schema(type=openapi.TYPE_STRING, description='Item ID'),
                            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description'),
                            'icompanyid': openapi.Schema(type=openapi.TYPE_STRING, description='Company ID'),
                            'info1': openapi.Schema(type=openapi.TYPE_STRING, description='Additional info 1'),
                            'info2': openapi.Schema(type=openapi.TYPE_STRING, description='Additional info 2')
                        }
                    )
                )
            ),
            201: openapi.Response(description='Item specification saved successfully'),
            400: openapi.Response(description='Company ID and Item ID are required'),
            404: openapi.Response(description='No item specifications found'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        """
        Handle POST request to retrieve and save item specifications.

        Parameters:
        - request (HttpRequest): The request object containing the payload with `item_id`.

        Returns:
        - Response: A list of item specifications matching the `ICompanyID` of the logged-in user and `ItemID` provided in the payload,
                    or a success message after saving a new item specification.
        """
        data = request.data
        item_id = data.get('item_id')

        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid

        if not icompanyid or not item_id:
            return Response({'error': 'Company ID and Item ID are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if all(key in data for key in ['specid', 'description', 'info1', 'info2']):
                # Save the item specification
                item_spec = ItemSpec(
                    specid=data['specid'],
                    itemid=item_id,
                    description=data['description'],
                    icompanyid=icompanyid,
                    info1=data['info1'],
                    info2=data['info2']
                )
                item_spec.save()
                return Response({'message': 'Item specification saved successfully'}, status=status.HTTP_201_CREATED)
            else:
                item_specs = ItemSpec.objects.filter(icompanyid=icompanyid, itemid=item_id)
                serializer = ItemSpecSerializer(item_specs, many=True)

                if not item_specs:
                    return Response({'error': 'No item specifications found'}, status=status.HTTP_404_NOT_FOUND)
                response_data = {
                    "message": "Success",
                    "data": {
                        "item_specs": serializer.data,
                    }}
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RateListView(APIView):
    """
    API View to retrieve item rates based on the company ID, item ID, and preferences.

    This view handles POST requests to filter and retrieve item rates from the database based on the `ICompanyID`
    of the logged-in user, the `ItemID`, and the `prefs` provided in the request payload.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve item rates",
        operation_description="Retrieve item rates based on the company ID, item ID, and preferences.",
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
                'item_id': openapi.Schema(type=openapi.TYPE_STRING, description='Item ID', example='ITEM123'),
                'prefs': openapi.Schema(type=openapi.TYPE_STRING, description='Preferences', enum=['Yes', 'No']),
            },
            required=['item_id', 'prefs']
        ),
        responses={
            200: openapi.Response(
                description='A list of item rates',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'AccCode': openapi.Schema(type=openapi.TYPE_STRING, description='Account Code'),
                                    'IPrefix': openapi.Schema(type=openapi.TYPE_STRING, description='IPrefix'),
                                    'MinQty': openapi.Schema(type=openapi.TYPE_NUMBER, description='Minimum Quantity'),
                                    'MaxQty': openapi.Schema(type=openapi.TYPE_NUMBER, description='Maximum Quantity'),
                                    'Rate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rate'),
                                    'ThousandRate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Thousand Rate'),
                                    'JobNo': openapi.Schema(type=openapi.TYPE_STRING, description='Job Number'),
                                    'ItemDesc': openapi.Schema(type=openapi.TYPE_STRING, description='Item Description'),
                                    'Quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity'),
                                    'RateInThousand': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rate in Thousand'),
                                    'RateUnit': openapi.Schema(type=openapi.TYPE_STRING, description='Rate Unit')
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(description='Company ID and Item ID are required'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        """
        Handle POST request to retrieve item rates based on company ID, item ID, and preferences.

        Parameters:
        - request (HttpRequest): The request object containing the payload with `item_id` and `prefs`.

        Returns:
        - Response: A list of item rates matching the `ICompanyID` of the logged-in user and `ItemID` provided in the payload,
                    or an error message.
        """
        try:
            data = request.data
            item_id = data.get('item_id')
            prefs = data.get('prefs')

            user = GetUserData.get_user(request)
            icompanyid = user.icompanyid

            if not icompanyid or not item_id:
                return Response({'error': 'Company ID and Item ID are required'}, status=status.HTTP_400_BAD_REQUEST)

            if prefs == "Yes":
                query = """
                        SELECT b.acccode AS AccCode, b.iprefix AS IPrefix, a.MinQty, a.MaxQty, a.Rate, a.thousandrate AS ThousandRate 
                        FROM item_ratelist AS a
                        JOIN Item_fpmasterext AS b ON a.Itemid = b.productid 
                        WHERE b.groupid = '00008' AND b.isactive != '0' 
                        AND a.Itemid = %s AND b.icompanyid = %s;
                        """
                params = [item_id, icompanyid]
            elif prefs == "No":
                query = """
                       SELECT JobNo, ItemDesc, Quantity, Rate, RateInThousand, RateUnit 
                       FROM item_wodetail 
                       WHERE itemid = %s AND IsActive = '0' 
                       AND IcompanyID = %s 
                       LIMIT 5;
                        """
                params = [item_id, icompanyid]
            else:
                return Response({'error': 'Invalid prefs value'}, status=status.HTTP_400_BAD_REQUEST)

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            response_data = {
                "message": "Success",
                "data": data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class SaveWithSeriesView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Save data with an auto-generated series ID",
        operation_description="This endpoint increments the docno in the Seriesmaster table and uses the new docno to save data in other tables.",
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
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='Series ID', example='532'),
            },
            required=['id']
        ),
        responses={
            201: openapi.Response(
                description='Data saved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'woid': openapi.Schema(type=openapi.TYPE_STRING, description='Generated series ID')
                    }
                )
            ),
            400: openapi.Response(description='Invalid prefix or company ID'),
            404: openapi.Response(description='Seriesmaster record not found'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        data=request.data

        id = data.get('id')

        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid

        serializer = SeriesMasterSaveSerializer(data=data, context={'request': request, 'icompanyid': icompanyid,'id':id})

        if serializer.is_valid():
            new_woid = serializer.save()

            return Response(
                {'message': 'Data saved successfully', 'new_woid':new_woid},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WOCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create Work Order",
        operation_description="Create Work Order and related records.",
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
            properties = {
    'pi_master_data': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invno': openapi.Schema(type=openapi.TYPE_STRING, description='Invoice Number', max_length=10, example='INV123'),
            'invdate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Invoice Date', example='2023-07-01T12:00:00Z'),
            'pono': openapi.Schema(type=openapi.TYPE_STRING, description='PO Number', max_length=30, example='PO123'),
            'podate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='PO Date', example='2023-07-01T12:00:00Z'),
            'clientid': openapi.Schema(type=openapi.TYPE_STRING, description='Client ID', max_length=10, example='CLIENT123'),
            'execid': openapi.Schema(type=openapi.TYPE_STRING, description='Exec ID', max_length=20, example='EXEC123'),
            'orderedby': openapi.Schema(type=openapi.TYPE_STRING, description='Ordered By', max_length=45, example='John Doe'),
            'shipvia': openapi.Schema(type=openapi.TYPE_STRING, description='Ship Via', max_length=50, example='Courier'),
            # 'paymentday': openapi.Schema(type=openapi.TYPE_STRING, description='Payment Day', max_length=50, example='30 Days'),
            # 'paymenttype': openapi.Schema(type=openapi.TYPE_STRING, description='Payment Type', max_length=100, example='Credit'),
            'remarks': openapi.Schema(type=openapi.TYPE_STRING, description='Remarks', max_length=100, example='Some remarks'),
            # 'muid': openapi.Schema(type=openapi.TYPE_STRING, description='MUID', max_length=10, example='MUID123'),
            # 'mdatetime': openapi.Schema(type=openapi.TYPE_STRING, description='M DateTime', max_length=45, example='2023-07-01T12:00:00Z'),
            # 'duid': openapi.Schema(type=openapi.TYPE_STRING, description='DUID', max_length=10, example='DUID123'),
            # 'ddatetime': openapi.Schema(type=openapi.TYPE_STRING, description='D DateTime', max_length=45, example='2023-07-01T12:00:00Z'),
            # 'filelocation': openapi.Schema(type=openapi.TYPE_STRING, description='File Location', max_length=225, example='/path/to/file'),
            'deliveryaddressid': openapi.Schema(type=openapi.TYPE_STRING, description='Delivery Address ID', max_length=10, example='ADDR123'),
            'deliveryaddress': openapi.Schema(type=openapi.TYPE_STRING, description='Delivery Address', max_length=100, example='123 Main St'),
            'taxid': openapi.Schema(type=openapi.TYPE_INTEGER, description='Tax ID', example=1),
            'terms': openapi.Schema(type=openapi.TYPE_STRING, description='Terms', max_length=100, example='Net 30'),
            # 'ratetype': openapi.Schema(type=openapi.TYPE_STRING, description='Rate Type', max_length=5, example='Fixed'),
            'basicamount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Basic Amount', example=1000.0),
            'freight': openapi.Schema(type=openapi.TYPE_NUMBER, description='Freight', example=50.0),
            'insurance': openapi.Schema(type=openapi.TYPE_NUMBER, description='Insurance', example=25.0),
            'totalamt': openapi.Schema(type=openapi.TYPE_NUMBER, description='Total Amount', example=1075.0),
            'seriesid': openapi.Schema(type=openapi.TYPE_STRING, description='Series ID', max_length=10, example='SERIES123')
        },
        required=['podate', 'clientid']
    ),
    'pi_detail_data': openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rowno': openapi.Schema(type=openapi.TYPE_INTEGER, description='Row Number', example=1),
                'itemid': openapi.Schema(type=openapi.TYPE_STRING, description='Item ID', max_length=10, example='ITEM123'),
                'itemcode': openapi.Schema(type=openapi.TYPE_STRING, description='Item Code', max_length=40, example='ITEMCODE123'),
                'codeno': openapi.Schema(type=openapi.TYPE_STRING, description='Code Number', max_length=45, example='CODE123'),
                'itemdesc': openapi.Schema(type=openapi.TYPE_STRING, description='Item Description', max_length=1000, example='Item Description'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity', example=100),
                'percentvar': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percent Variation', example=2.5),
                'qtyplus': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity Plus', example=10),
                'qtyminus': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity Minus', example=5),
                'unitid': openapi.Schema(type=openapi.TYPE_STRING, description='Unit ID', max_length=10, example='UNIT123'),
                'rate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rate', example=10.5),
                'rateunit': openapi.Schema(type=openapi.TYPE_STRING, description='Rate Unit', max_length=10, example='INR / USD'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount', example=1050.75),
                'freight': openapi.Schema(type=openapi.TYPE_NUMBER, description='Freight', example=0.0),
                'insurance': openapi.Schema(type=openapi.TYPE_NUMBER, description='Insurance', example=0.0),
                'specification': openapi.Schema(type=openapi.TYPE_STRING, description='Specification', max_length=10, example='SPEC123'),
                'remarks': openapi.Schema(type=openapi.TYPE_STRING, description='Remarks', max_length=1000, example='Some remarks'),
                'hold': openapi.Schema(type=openapi.TYPE_INTEGER, description='Hold', example=0),
                'clstatus': openapi.Schema(type=openapi.TYPE_INTEGER, description='CL Status', example=0),
                'approved': openapi.Schema(type=openapi.TYPE_NUMBER, description='Approved', example=1.0),
                'approvedby': openapi.Schema(type=openapi.TYPE_STRING, description='Approved By', max_length=45, example='Manager'),
                'approvaldate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Approval Date', example='2023-07-01T12:00:00Z'),
                'invoiceqty': openapi.Schema(type=openapi.TYPE_NUMBER, description='Invoice Quantity', example=100.0),
                'constatus': openapi.Schema(type=openapi.TYPE_STRING, description='Con Status', max_length=200, example='Confirmed'),
                'lastupdatedon': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Last Updated On', example='2023-07-01T12:00:00Z'),
                'templateid': openapi.Schema(type=openapi.TYPE_STRING, description='Template ID', max_length=20, example='TEMPLATE123'),
                'rateinthousand': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rate in Thousand', example=10000.0),
                'extra1': openapi.Schema(type=openapi.TYPE_STRING, description='Extra1', max_length=100, example='Extra1'),
                'extra2': openapi.Schema(type=openapi.TYPE_STRING, description='Extra2', max_length=100, example='Extra2'),
                'extra3': openapi.Schema(type=openapi.TYPE_STRING, description='Extra3', max_length=100, example='Extra3'),
                'extra4': openapi.Schema(type=openapi.TYPE_STRING, description='Extra4', max_length=100, example='Extra4'),
                'extra5': openapi.Schema(type=openapi.TYPE_STRING, description='Extra5', max_length=100, example='Extra5'),
                'closedate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Close Date', example='2023-07-01T12:00:00Z'),
                'closeby': openapi.Schema(type=openapi.TYPE_STRING, description='Close By', max_length=10, example='Admin'),
                'closereason': openapi.Schema(type=openapi.TYPE_STRING, description='Close Reason', max_length=250, example='Completion'),
                'orderqty': openapi.Schema(type=openapi.TYPE_INTEGER, description='Order Quantity', example=100)
            },
            required=['rowno', 'itemid', 'quantity', 'rate', 'amount']
                )
            )
        }   ,
            required=['wo_master_data', 'wo_detail_data']
        ),
        responses={
            201: openapi.Response(
                description='Data saved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'new_woid': openapi.Schema(type=openapi.TYPE_STRING, description='New Work Order ID')
                    }
                )
            ),
            400: openapi.Response(description='Bad request'),
            401: openapi.Response(description='Unauthorized'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        data = request.data
        user = GetUserData.get_user(request)
        auid = user.id
        icompanyid = user.icompanyid
        print(auid,icompanyid)
        print("auid,icompanyid")
        seriesid = data.get('pi_master_data').get('seriesid')

        
        # below only the serializer data id given because the id is req .
        series_serializer = SeriesMasterSaveSerializer(data={'id' : data.get('pi_master_data').get('seriesid')}, context={'request': request, 'icompanyid': icompanyid,'id': seriesid})
        if series_serializer.is_valid():
            try:
                with transaction.atomic():
                    # Needed data for itemwomaster
                    # new_woid = series_serializer.save()
                    instance = series_serializer.save()


                    new_woid = series_serializer.context.get('new_woid')
                    prefix = series_serializer.context.get('prefix')
                    current_docno = series_serializer.context.get('current_docno')
                    sufix = series_serializer.context.get('ssufix')

                    docnotion = 25 # this will be set after march , generate accordingly

                    print(new_woid,current_docno)
                    #End Item wo master

                    # Add the new_woid to the wo_master_data and wo_detail_data
                    data['pi_master_data']['icompanyid'] = icompanyid
                    data['pi_master_data']['docid'] = new_woid
                    data['pi_master_data']['invno'] = current_docno
                    data['pi_master_data']['sprefix'] = prefix
                    data['pi_master_data']['ssufix'] = sufix
                    data['pi_master_data']['docnotion'] = docnotion
                    data['pi_master_data']['isactive'] = 1
                    data['pi_master_data']['auid'] = auid

                    # data['wo_detail_data']['woid'] = docnotion
                    for index, detail in enumerate(data['pi_detail_data']):
                    # for detail in data['wo_detail_data']:
                        detail['docid'] = new_woid
                        detail['icompanyid'] = icompanyid
                        detail['jobno'] =  str(new_woid) + "-"+ str(index + 1)
                        detail['docnotion'] = docnotion
                        detail['isactive'] = 1
                    # Save the item_womaster data
                    wo_master_data = data['pi_master_data']
                    # print(wo_master_data)
                    
                    wo_master_serializer = ItemPiMasterSerializer(data=wo_master_data)
                    if wo_master_serializer.is_valid():
                        wo_master_serializer.save()
                    else:
                        raise serializers.ValidationError(wo_master_serializer.errors)

                    # Save the item_wodetail data
                    for detail in data['pi_detail_data']:
                        wo_detail_serializer = ItemPiDetailSerializer(data=detail)
                        if wo_detail_serializer.is_valid():
                            wo_detail_serializer.save()
                        else:
                            raise serializers.ValidationError(wo_detail_serializer.errors)
                    #####################
                    #     # Save the companydelqtydate data
                    #     for del_address in detail['del_address']:
                    #         del_qty_date_serializer = CompanyDelQtyDateSerializer(data=del_address)
                    #         if del_qty_date_serializer.is_valid():
                    #             del_qty_date_serializer.save()
                    #         else:
                    #             raise serializers.ValidationError(del_qty_date_serializer.errors)

                return Response(
                    {'message': 'Data saved successfully', 'new_woid': new_woid},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(series_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WoListAPIView(APIView):
    """
    API endpoint to retrieve a list of Work Orders based on various filters.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve List of Work Orders",
        operation_description="Retrieve a list of Work Orders based on filters.",
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
                'txt_docid': openapi.Schema(type=openapi.TYPE_STRING, description='Search by Work Order ID (partial match)'),
                'txt_miscodeNo': openapi.Schema(type=openapi.TYPE_STRING, description='Search by MIS Code Number (partial match)'),
                'txt_productName': openapi.Schema(type=openapi.TYPE_STRING, description='Search by Product Name (partial match)'),
                'txt_ClientCode': openapi.Schema(type=openapi.TYPE_STRING, description='Search by Client Code (partial match)'),
                'drp_ClientId': openapi.Schema(type=openapi.TYPE_STRING, description='Filter by Client ID'),
                'docnotion': openapi.Schema(type=openapi.TYPE_INTEGER, description='Filter by Doc Notion', enum=[1, 2, 3]),  # Adjust enum values as per your requirement
                'limit': openapi.Schema(type=openapi.TYPE_INTEGER, description='Limit number of results'),
            }
        ),
        responses={
            200: openapi.Response(
                description='Data retrieved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'wo_list': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'WOID': openapi.Schema(type=openapi.TYPE_STRING),
                                            'WODate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                            'WONo': openapi.Schema(type=openapi.TYPE_STRING),
                                            'CompanyName': openapi.Schema(type=openapi.TYPE_STRING),
                                        }
                                    )
                                )
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description='Bad request'),
            401: openapi.Response(description='Unauthorized'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request, format=None):
        """
        Retrieve a list of Work Orders based on the provided filters.
        """
        data = request.data
        filters = ""

        # Get user data using your utility method
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid

        # Apply filters based on request data
        docid = data.get('txt_docid', None)
        if docid:
            filters += f" AND a.docid LIKE '%{docid}%'"

        miscodeNo = data.get('txt_miscodeNo', None)
        if miscodeNo:
            filters += f" AND d.AccCode LIKE '%{miscodeNo}%'"
        
        productName = data.get('txt_productName', None)
        if productName:
            filters += f" AND d.Description LIKE '%{productName}%'"
        
        clientCode = data.get('txt_ClientCode', None)
        if clientCode:
            filters += f" AND d.IPrefix LIKE '%{clientCode}%'"

        clientId = data.get('drp_ClientId', None)
        if clientId:
            filters += f" AND a.ClientID = '{clientId}'"

        docnotion = data.get('docnotion', None)
        if docnotion is None:
            return Response(
                {"error": True, "message": "docnotion parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        filters += f" AND a.docnotion = {int(docnotion)}"
        filters += f" AND a.ICompanyID = '{icompanyid}'"

        limit = data.get('limit', None)
        limitQ = f" LIMIT {limit}" if limit else ""
        
        query = f"""
            SELECT a.docid, MAX(date_format(a.invdate, '%d/%m/%Y')) AS invdate, a.invno, Get_CompanyName(a.ClientId) AS CompanyName
            FROM item_pi_master AS a
            JOIN item_pi_detail AS b ON a.docid = b.docid
            JOIN item_fpmasterext AS d ON b.ItemID = d.productid
            WHERE 1=1 {filters}
            GROUP BY b.docid, a.invno
            ORDER BY a.invdate DESC {limitQ};
        """
        # print(query)

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            response_data = {
                "message": "Success",
                "data": {
                    "pi_list": result,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except DatabaseError as e:
            return Response(
                {"message": "Internal Server Error, Contact Administration", "errorMessage": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class WoJobListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve Work Order details by WOID",
        operation_description="Retrieve Work Order details by Work Order ID.",
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
                'docid': openapi.Schema(type=openapi.TYPE_STRING, description='Proforma Invoice ID'),
            },
            required=['docid']
        ),
        responses={
            200: openapi.Response(
                description='Success',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Error flag'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Response message'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'woid': openapi.Schema(type=openapi.TYPE_STRING, description='Work Order ID'),
                                    'jobno': openapi.Schema(type=openapi.TYPE_INTEGER, description='Job Number'),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING, description='Item Description'),
                                    'acccode': openapi.Schema(type=openapi.TYPE_STRING, description='Account Code'),
                                    'iprefix': openapi.Schema(type=openapi.TYPE_STRING, description='Item Prefix'),
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(description='Bad request'),
            401: openapi.Response(description='Unauthorized'),
            404: openapi.Response(description='Not found'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request, format=None):
        docid = request.data.get('docid', None)
        
        if not docid:
            return Response(
                {"error": True, "message": "docid parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        query = """
            SELECT a.Docid, b.Description, b.AccCode, b.IPrefix
            FROM item_pi_detail as a
            JOIN item_fpmasterext as b ON a.ItemID = b.ProductID
            WHERE a.Docid = %s;
        """

        # print(query)

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [docid])
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]

            response_data = {
                    "message": "Success",
                    "data": {
                        "pi_data": result,
                    }}
            return Response(response_data, status=status.HTTP_200_OK)

        except DatabaseError as e:
            return Response(
                {"message": "Internal Serval Error, Contact Administration", "errorMessage" : str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WoListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve Proforma Invoice Data",
        operation_description="Fetch data from Item_pi_Detail, item_pi_master tables using docid and icompanyid.",
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
                'docid': openapi.Schema(type=openapi.TYPE_STRING, description='Work Order ID'),
            },
            required=['docid']
        ),
        responses={
            200: openapi.Response(
                description='Data fetched successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'pi_data': openapi.Schema(type=openapi.TYPE_OBJECT)
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description='Bad request'),
            401: openapi.Response(description='Unauthorized'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request, format=None):
        docid = request.data.get('docid')
        user = request.user
        icompanyid = user.icompanyid

        if not docid or not icompanyid:
            return Response(
                {"error": True, "message": "docid and icompanyid parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item_pi_wodetail_qs = ItemPiDetail.objects.filter(docid=docid, icompanyid=icompanyid)
            item_pi_womaster_qs = ItemPiMaster.objects.filter(docid=docid, icompanyid=icompanyid)

            item_pi_wodetail_serializer = ItemWodetailSerializer(item_pi_wodetail_qs, many=True)
            item_pi_womaster_serializer = ItemWomasterSerializer(item_pi_womaster_qs, many=True)

            result = {
                "pi_master_data": item_pi_womaster_serializer.data,
                "pi_detail_data": item_pi_wodetail_serializer.data,
            }

            response_data = {
                "message": "Success",
                "data": {
                    "pi_data": result,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Internal Server Error", "errorMessage": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompanyListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve Company Master Data",
        operation_description="Fetch a list of active companies ordered by their name for the authenticated user's company.",
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
            200: openapi.Response(
                description='Data fetched successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'companies': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))
                            }
                        )
                    }
                )
            ),
            401: openapi.Response(description='Unauthorized'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Proforma Invoice / Workorder']
    )
    def get(self, request, format=None):
        try:
            user = GetUserData.get_user(request)
            icompanyid = user.icompanyid

            # companies = Companymaster.objects.filter(companyid=icompanyid, isactive=True).order_by('companyname')
            companies = Companymaster.objects.filter(isactive=True).order_by('companyname')
            companies_results = ExtendedCompanySerializer(companies, many=True).data

            response_data = {
                "message": "Success",
                "data": {
                    "companies": companies_results,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Companymaster.DoesNotExist:
            return Response(
                {"message": "No active companies found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": "Internal Server Error", "errorMessage": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WoRegisterView(APIView):
    """
    API View to process a JSON payload and call the insert_into_WOdetail_WORegister_new stored procedure.
    This endpoint validates the provided parameters, calls the stored procedure, and returns the result as a JSON response.

    Authentication:
        - JWT Authentication
        - Requires the user to be authenticated and have staff permissions.

    Required Payload:
        - PICompanyID (string): Company ID
        - from_date (string): Start date in YYYY-MM-DD format
        - to_date (string): End date in YYYY-MM-DD format
        - order_type (integer): Order type
        - report_no (integer): Report number
        - postatus (string): PO status
        - closeper (integer): Close percentage
        - isexpdeldate (integer): Expected delivery date flag (0 or 1)
        - edate (string): End date
        - client_name (string): Client name
        - marketing_executive (string): Marketing executive ID
        - pclass (string): Class
        - view_p (string): View parameter
        - param_p (string): Parameter P

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
        operation_description="Process a JSON payload and call the insert_into_WOdetail_WORegister_new stored procedure.",
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
                'PICompanyID': openapi.Schema(type=openapi.TYPE_STRING, description='Company ID'),
                'from_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='From Date (YYYY-MM-DD)'),
                'to_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='To Date (YYYY-MM-DD)'),
                'order_type': openapi.Schema(type=openapi.TYPE_INTEGER, description='Order Type'),
                'report_no': openapi.Schema(type=openapi.TYPE_INTEGER, description='Report Number'),
                'postatus': openapi.Schema(type=openapi.TYPE_STRING, description='PO Status'),
                'closeper': openapi.Schema(type=openapi.TYPE_INTEGER, description='Close Percentage'),
                'isexpdeldate': openapi.Schema(type=openapi.TYPE_INTEGER, description='Expected Delivery Date Flag (0 or 1)'),
                'edate': openapi.Schema(type=openapi.TYPE_STRING, description='End Date'),
                'client_name': openapi.Schema(type=openapi.TYPE_STRING, description='Client Name'),
                'marketing_executive': openapi.Schema(type=openapi.TYPE_STRING, description='Marketing Executive ID'),
                'pclass': openapi.Schema(type=openapi.TYPE_STRING, description='Class'),
                'view_p': openapi.Schema(type=openapi.TYPE_STRING, description='View Parameter'),
                'param_p': openapi.Schema(type=openapi.TYPE_STRING, description='Parameter P')
            },
            example={
                'PICompanyID': '00001',
                'from_date': '2024-04-01',
                'to_date': '2024-07-23',
                'order_type': 0,
                'report_no': 1,
                'postatus': 'All Records',
                'closeper': 0,
                'isexpdeldate': 0,
                'edate': '0',
                'client_name': '0',
                'marketing_executive': '0',
                'pclass': '0',
                'view_p': '',
                'param_p': ''
            }
        ),
        responses={
            200: 'Data processed successfully',
            400: 'Invalid input data',
            401: 'Unauthorized: Invalid access token',
            500: 'Failed to process the data. Please try again later.'
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        """
        Handle POST request to process the JSON payload and call a stored procedure.

        Validates the provided parameters, calls the insert_into_WOdetail_WORegister_new stored procedure,
        and returns the result as a JSON response.

        Args:
            request (HttpRequest): The request object containing the JSON payload.

        Returns:
            Response: The data from the stored procedure or an error message.
        """
        payload = request.data
        required_fields = ['PICompanyID', 'from_date', 'to_date', 'order_type', 'report_no', 'postatus', 'closeper', 'isexpdeldate', 'edate', 'client_name', 'marketing_executive', 'pclass', 'view_p', 'param_p']
        
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return Response({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

        PICompanyID = payload['PICompanyID']
        from_date = payload['from_date']
        to_date = payload['to_date']
        order_type = payload['order_type']
        report_no = payload['report_no']
        postatus = payload['postatus']
        closeper = payload['closeper']
        isexpdeldate = payload['isexpdeldate']
        edate = payload['edate']
        client_name = payload['client_name']
        marketing_executive = payload['marketing_executive']
        pclass = payload['pclass']
        view_p = payload['view_p']
        param_p = payload['param_p']

        try:
            with connection.cursor() as cursor:
                cursor.callproc('insert_into_WOdetail_WORegister_new', [PICompanyID, from_date, to_date, order_type, report_no, postatus, closeper, isexpdeldate, edate, client_name, marketing_executive, pclass, view_p, param_p])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchmany(50)]#cursor.fetchall() #for all
                print(results)
            
            response_data = {
                "message": "Success",
                "data": results
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# End Order Management Section 

#For print view

class PrintPIDataView(APIView):
    """
    View to call Cr_Print_PI_Data stored procedure with an invoice number.
    Accessible only to authenticated users.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Retrieve PI Data",
        operation_description="Calls the Cr_Print_PI_Data stored procedure with the provided invoice number.",
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
                'invoice_no': openapi.Schema(type=openapi.TYPE_STRING, description='Invoice number to call the stored procedure'),
            },
            required=['invoice_no'],
            example={"invoice_no": "SSGI/PFI/23-24/0001"}
        ),
        responses={
            200: "Success",
            400: "Invalid input data",
            401: "Unauthorized",
            500: "Internal server error"
        },
        tags=['Proforma Invoice / Workorder']
    )
    def post(self, request):
        invoice_no = request.data.get('invoice_no')
        print(invoice_no)
        if not invoice_no:
            return Response({"error": "Invoice number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.callproc('Cr_Print_PI_Data', [invoice_no])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print(results[0])
                pdf_buffer = __gen_pdf__(results[0])
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Proforma_Invoice_{invoice_no}.pdf"'
            return response

        except Exception as e:
            error_message = f"Failed to retrieve PI data: {str(e)}"
            return Response({"message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#End print view
