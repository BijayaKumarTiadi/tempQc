## Work order Imports
#--Default imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import json
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import connection, connections
from django.core.exceptions import ObjectDoesNotExist

#--custome imports
from .permissions import ViewByStaffOnlyPermission
from accounts.helpers import GetUserData

from .models import ItemWomaster
from .utils import DataManager
from .helper import pdf_processing, gemini_1
from mastersapp.models import Seriesmaster
from mastersapp.models import Companymaster
from mastersapp.models import Employeemaster
from mastersapp.models import CompanymasterEx1
from .models import Paymentterms


#-- serializers
from .serializers import SeriesSerializer
from .serializers import CompanySerializer
from .serializers import EmployeeSerializer
from .serializers import PaymentTermsSerializer
from .serializers import CompanyEx1Serializer

#--Installed Library imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# AIPO Section
"""
- > The Database will be the default database . Make sure to change the database accordingly . 
- > Some API Keys from Gemini inserted to setting , Make sure thats working fine .
- > For now there is not local llm implimented .
- > Database queries at utils.py and the AI calls at helper.py , Formats at format.json .
- > Remember you need to install poppler to use this tool . Download link : https://github.com/oschwartz10612/poppler-windows/releases version : 24.02.0-0
- > Permission Classes need to be changed .
- > End of this AIPO there is no dependencies of thease views .
- > Independent Releases of this app is at : https://github.com/BijayaKumarTiadi/aipo/tree/aipo-rest
- > This using google-generativeai==0.5.2 .
"""
class ProcessPDFView(APIView):
    """
    API View to process a PDF file and return the parsed data.
    """

    permission_classes = [AllowAny]

    parser_classes = [MultiPartParser]
    @swagger_auto_schema(
        operation_summary="Upload PDF and extract text",
        operation_description="Upload a PDF file and extract its text content.",
        manual_parameters=[
            openapi.Parameter(
                name='companyname',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                description='The company name',
                required=True,
                format='company name'
            ),
            openapi.Parameter(
                name='pdf_file',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='PDF file to upload',
                required=True
            )
        ],
        responses={
            200: 'Text extracted successfully',
            400: 'Invalid input data',
            401: 'Unauthorized: Invalid access token',
            500: 'Failed to process the data. Please try again later.'
        },
        tags=['Order Management / AIPO']
    )
    def post(self, request):
        """
        Handle POST request to process the uploaded PDF file.

        Args:
            request (HttpRequest): The request object containing the PDF file and company name.

        Returns:
            Response: The parsed data or an error message.
        """
        pdf_file = request.FILES.get('pdfFile')
        company_name = request.data.get('companyName')
        if not pdf_file or not company_name:
            return Response({"error": "PDF file and company name are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pdf_text = pdf_processing(pdf_file)
            json_file_path = os.path.join(os.path.dirname(__file__), 'format.json')
            with open(json_file_path) as json_file:
                company_formats = json.load(json_file)

            company_format = company_formats['company_formats'].get(company_name)
            if not company_format:
                return Response({"error": "Company format not found."}, status=status.HTTP_400_BAD_REQUEST)

            data = gemini_1(pdf_text, company_format).replace("'", '"').replace("None", 'null').replace("```json","").replace("```","")
            parsed_data = json.loads(data)

            #Check PO Available 
            po_number = parsed_data.get('po_number')
            if po_number:
                po_exists = ItemWomaster.objects.filter(wono=po_number).exists()
                parsed_data['PO_AVAILABLE'] = po_exists
            else:
                parsed_data['PO_AVAILABLE'] = False
            #End PO

            data_manager = DataManager()
            items = data_manager.get_itemcodes(parsed_data)
            product_ids = data_manager.validate_itemcode(items)

            for item in parsed_data['items']:
                item_code = item.get('item_code')
                product_id = product_ids.get(item_code)
                if product_id:
                    item['productID'] = product_id
                else:
                    item['productID'] = None


            return Response(parsed_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error on ProcessPDFView :": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaveResponseView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Save Response Data",
        operation_description="Save response data to the database.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
           properties={
                    'json_data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'company_name': openapi.Schema(type=openapi.TYPE_STRING, description="Company name"),
                            'po_number': openapi.Schema(type=openapi.TYPE_STRING, description="PO number"),
                            # Add other properties as needed
                        },
                        required=['company_name', 'po_number']  # Specify required properties
                    ),
                    'userid': openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID."),
                    'icompanyid': openapi.Schema(type=openapi.TYPE_INTEGER, description="ICompany ID."),
                    'clientid': openapi.Schema(type=openapi.TYPE_INTEGER, description="Client ID."),
                    'company_address_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Company address ID.")
                },
            required=['po_number','json_data']
        ),
        responses={
            200: openapi.Response(description='Data saved successfully'),
            400: openapi.Response(description='Invalid input data'),
            500: openapi.Response(description='Failed to save the data. Please try again later.')
        },
        tags=['Order Management / AIPO']
    )
    def post(self, request):
        """
        Handle POST request to save response data to the database.

        Args:
            request (HttpRequest): The request object containing the response data.

        Returns:
            Response: A status message indicating the success or failure of the operation.
        """
        parsed_data = request.data.get('json_data')
        userid = request.data.get('userid')
        icompanyid = request.data.get('icompanyid')
        clientid = request.data.get('clientid')
        company_address_id = request.data.get('company_address_id')
        po_number = parsed_data.get('po_number')

        #Validate those data
        if not parsed_data:
            return Response({"error": "json_data is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not userid:
            return Response({"error": "userid is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not icompanyid:
            return Response({"error": "icompanyid is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not clientid:
            return Response({"error": "clientid is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not company_address_id:
            return Response({"error": "company_address_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not po_number:
                return Response({"error": "PO number is required."}, status=status.HTTP_400_BAD_REQUEST)
        #End Validate

        try:
            po_exists = ItemWomaster.objects.filter(wono=po_number).exists()
            if po_exists:
                return Response({"status": "PO is already available inside the database."}, status=status.HTTP_200_OK)

            data_manager = DataManager()
            return_resp = data_manager.insert_to_temp_table(parsed_data, userid=userid, icompanyid=icompanyid,clientid=clientid, company_address_id=company_address_id)

            return Response({"status": "Data saved successfully", "data": return_resp}, status=status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"error": f"Validation error: {ve}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An internal error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetCompanyFormatsView(APIView):
    """
    API View to get company formats.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get company formats",
        operation_description="Get the list of company formats from the format.json file.",
        responses={
            200: openapi.Response(
                description='List of company formats',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING)
                )
            ),
            400: openapi.Response(description='Invalid input data'),
            500: openapi.Response(description='Failed to load company formats')
        },
        tags=['Order Management / AIPO']
    )
    def get(self, request):
        """
        Handle GET request to return company formats.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: A list of company format keys or an error message.
        """
        try:
            json_file_path = os.path.join(os.path.dirname(__file__), 'format.json')
            with open(json_file_path) as json_file:
                company_formats = json.load(json_file)

            formats = list(company_formats['company_formats'].keys())
            return Response({"status": "Data fetched successfully", "data": formats}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e), "data": {} }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# End AIPO Section


# Order Management Section 
"""
Informations : ...
"""


class SeriesView(APIView):
    """
    API View to retrieve the list of active series for 'Work Order' documents for a specific company
    and list of active companies.

    This view requires JWT authentication and specific permissions to be accessed. The series are filtered
    by 'Work Order' document type, company ID, and their active status. The results are returned in descending
    order by ID.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Get active 'Work Order' series and active companies",
        operation_description="Retrieve the list of active series for 'Work Order' documents for the authenticated user's company and list of all active companies.",
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
                                    'Prefix': openapi.Schema(type=openapi.TYPE_STRING, description='Prefix of the series')
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
        tags=['Order Management / Workorder']
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
                doctype='Work Order',
                icompanyid=icompanyid,
                isactive=True
            ).order_by('-id')
            series_results = SeriesSerializer(series, many=True).data
            
            # Fetch active companies
            companies = Companymaster.objects.filter(isactive=True).order_by('companyname')
            companies_results = CompanySerializer(companies, many=True).data

            # Fetch active employees
            employees = Employeemaster.objects.filter(isactive=True).order_by('empname')
            employees_results = EmployeeSerializer(employees, many=True).data

            # Fetch active payment terms
            payment_terms = Paymentterms.objects.filter(isactive=True)
            payment_terms_results = PaymentTermsSerializer(payment_terms, many=True).data

            # Combine all responses
            response_data = {
                "message": "Success",
                "data": {
                'seriesresp': series_results,
                'companiesresp': companies_results,
                'marketingExe': employees_results,
                'pay_terms': payment_terms_results,
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
        operation_summary="Fetch client-related data",
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
        tags=['Order Management / Workorder']
    )
    def post(self, request):
        client_id = request.data.get('client_id')

        if not client_id:
            return Response({'error': 'Client ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch contact person details
            contact_person = CompanymasterEx1.objects.filter(companyid=client_id, isactive=True)
            contact_person_results = CompanyEx1Serializer(contact_person, many=True).data

            # Fetch payterms and marketing executive
            company_details = Companymaster.objects.filter(companyid=client_id, isactive=True).first()
            if not company_details:
                return Response({'error': 'No company found with the given ID'}, status=status.HTTP_404_NOT_FOUND)

            payterms = Paymentterms.objects.filter(payid=company_details.payid, isactive=True)
            payterms_results = PaymentTermsSerializer(payterms, many=True).data

            marketing_executive = Employeemaster.objects.filter(empid=company_details.repid, isactive=True)
            marketing_executive_results = EmployeeSerializer(marketing_executive, many=True).data

            # Combine all responses
            response_data = {
                "message": "Success",
                "data": {
                'contact_person': contact_person_results,
                'pay_terms': payterms_results,
                'marketing_executive': marketing_executive_results,
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
        tags=['Order Management / Workorder']
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
        tags=['Order Management / Workorder']
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
# End Order Management Section 