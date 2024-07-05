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
from django.db import connection, connections, DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers
#--custome imports
from .permissions import ViewByStaffOnlyPermission
from accounts.helpers import GetUserData

from .utils import DataManager
from .helper import pdf_processing, gemini_1
from mastersapp.models import ItemWomaster
from mastersapp.models import ItemWodetail, Seriesmaster
from mastersapp.models import Companymaster
from mastersapp.models import Employeemaster
from mastersapp.models import CompanymasterEx1
from mastersapp.models import Companydelqtydate
from .models import Paymentterms
from .models import ItemSpec
from .models import Mypref

#-- serializers
from .serializers import SeriesSerializer
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
from .serializers import CompanydelqtydateSerializer


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
        operation_summary="Get active 'Work Order' series and active companies  On Page Load Dropdown Lists . ",
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
                # isactive=True
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

            # Fetch prefs 
            mypref_load = Mypref.objects.filter(heading="WorkOrder")
            mypref_load_results = MyprefSerializer(mypref_load, many=True).data

            # Combine all responses
            response_data = {
                "message": "Success",
                "data": {
                'seriesresp': series_results,
                'companiesresp': companies_results,
                'marketingExe': employees_results,
                'pay_terms': payment_terms_results,
                'prefs': mypref_load_results,
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
        tags=['Order Management / Workorder']
    )
    def post(self, request):
        client_id = request.data.get('client_id')
        user = GetUserData.get_user(request)
        icompanyid = user.icompanyid # keeping for future reference

        if not client_id:
            return Response({'error': 'Company ID , Client ID is required'}, status=status.HTTP_400_BAD_REQUEST)

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
                'pay_terms': payterms_results,
                'marketing_executive': marketing_executive_results,
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
        tags=['Order Management / Workorder']
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
        tags=['Order Management / Workorder']
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
        tags=['Order Management / Workorder']
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
            properties={
                'wo_master_data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'SeriesID': openapi.Schema(type=openapi.TYPE_STRING, description='Series ID', example='SERIES123'),
                        'wodate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Work Order Date', example='2022-03-10 00:00:00'),
                        'clientid': openapi.Schema(type=openapi.TYPE_STRING, description='Client ID', example='CLIENT123'),
                        'postatus': openapi.Schema(type=openapi.TYPE_STRING, description='PO Status', example='Open'),
                        'wono': openapi.Schema(type=openapi.TYPE_STRING, description='Work Order Number', example='WO123'),
                        'podate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='PO Date', example='2024-06-25 22:16:44'),
                        'poreceivedate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='PO Recieve Date', example='2022-03-10 00:00:00'),
                        'execid': openapi.Schema(type=openapi.TYPE_STRING, description='Exec ID', example='EXEC123'),
                        'orderedby': openapi.Schema(type=openapi.TYPE_STRING, description='Ordered By', example='John Doe'),
                        'paymentday': openapi.Schema(type=openapi.TYPE_INTEGER, description='Payment Day', example=30),
                        'paymenttype': openapi.Schema(type=openapi.TYPE_STRING, description='Payment Type', example='Credit'),
                        'filelocation': openapi.Schema(type=openapi.TYPE_STRING, description='File Location', example='/path/to/file'),
                        'remarks': openapi.Schema(type=openapi.TYPE_STRING, description='Remarks', example='Some remarks'),
                        'proofingchk': openapi.Schema(type=openapi.TYPE_INTEGER, description='Proofing Check', example=1),
                        
                    },
                    required=['SeriesID', 'WODate', 'ClientId']
                ),
                'wo_detail_data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            # 'JobNo': openapi.Schema(type=openapi.TYPE_STRING, description='Job Number', example='JOB123'),
                            'itemdesc': openapi.Schema(type=openapi.TYPE_STRING, description='Item Description', example='Item Description'),
                            'itemcode': openapi.Schema(type=openapi.TYPE_STRING, description='Item Code', example='ITEM123'),
                            'codeno': openapi.Schema(type=openapi.TYPE_STRING, description='Code Number', example='CODE123'),
                            'itemid': openapi.Schema(type=openapi.TYPE_STRING, description='Item ID', example='ITEM123'),
                            'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity', example=100),
                            'qtyplus': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity Plus', example=10),
                            'qtyminus': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity Minus', example=5),
                            'rate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rate', example=10.5),
                            'actualrate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Actual Rate', example=10.5),
                            'unitid': openapi.Schema(type=openapi.TYPE_STRING, description='Unit ID', example='UNIT123'),
                            'rateinthousand': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rate in Thousand', example=10000),
                            'rateunit': openapi.Schema(type=openapi.TYPE_STRING, description='Rate Unit', example='kg'),
                            'artworkno': openapi.Schema(type=openapi.TYPE_STRING, description='Artwork Number', example='ART123'),
                            'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount', example=1050.75),
                            'percentvar': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percent Variation', example=2.5),
                            'freight': openapi.Schema(type=openapi.TYPE_STRING, description='Freight', example='0'),
                            'specification': openapi.Schema(type=openapi.TYPE_STRING, description='Specification', example='SPEC123'),
                            'ref': openapi.Schema(type=openapi.TYPE_STRING, description='Reference', example='REF123'),
                            'color': openapi.Schema(type=openapi.TYPE_STRING, description='Color', example='Red'),
                            'cp': openapi.Schema(type=openapi.TYPE_STRING, description='CP', example='P'),
                            'docnotion': openapi.Schema(type=openapi.TYPE_STRING, description='Doc Notion', example='DOC123'),
                            'remarks': openapi.Schema(type=openapi.TYPE_STRING, description='Remarks', example='Some remarks'),
                            'transfer_wo': openapi.Schema(type=openapi.TYPE_INTEGER, description='Transfer WO', example=0),
                            'hold': openapi.Schema(type=openapi.TYPE_INTEGER, description='Hold', example=0),
                            'dontshowforjc': openapi.Schema(type=openapi.TYPE_INTEGER, description='Don\'t Show for JC', example=0),
                            'artworkreceive': openapi.Schema(type=openapi.TYPE_INTEGER, description='Artwork Received', example=0),
                            'closedate': openapi.Schema(type=openapi.TYPE_STRING, description='Closed', format=openapi.FORMAT_DATE, example='2060-01-01 00:00:00'),
                            'templateid': openapi.Schema(type=openapi.TYPE_STRING, description='Template ID', example='TEMPLATE123'),
                            'rowno': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rowno', example=0),
                            'del_address': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'recordid_old': openapi.Schema(type=openapi.TYPE_STRING, description='Old Record ID', example='OLD123'),
                                        'JobNo': openapi.Schema(type=openapi.TYPE_STRING, description='Job Number', example='JOB123'),
                                        'clientid': openapi.Schema(type=openapi.TYPE_STRING, description='Client ID', example='CLIENT123'),
                                        'delrecordid': openapi.Schema(type=openapi.TYPE_STRING, description='Delivery Record ID', example='DEL123'),
                                        'billingrecordid': openapi.Schema(type=openapi.TYPE_STRING, description='Billing Record ID', example='BILL123'),
                                        'schdeliverydate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Scheduled Delivery Date', example='2022-03-10 00:00:00'),
                                        'lastdeliverydate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Last Delivery Date', example='2022-03-10 00:00:00'),
                                        'qtytodeliver': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity Delivered', example=50),
                                        'specid': openapi.Schema(type=openapi.TYPE_STRING, description='Specification ID', example='SPEC123'),
                                        'itemid': openapi.Schema(type=openapi.TYPE_STRING, description='Item ID', example='ITEM123'),
                                        'qtydelivered': openapi.Schema(type=openapi.TYPE_NUMBER, description='Qty Delivered', example='0.00'),
                                        'Rowno': openapi.Schema(type=openapi.TYPE_INTEGER, description='ROW No', example='0'),
                                    }
                                )
                            )
                        }
                    )
                )
            },
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
        tags=['Order Management / Workorder']
    )
    def post(self, request):
        data = request.data
        user = request.user
        icompanyid = user.icompanyid
        id = data.get('wo_master_data').get('SeriesID')

        
        # below only the serializer data id given because the id is req .
        series_serializer = SeriesMasterSaveSerializer(data={'id' : data.get('wo_master_data').get('SeriesID')}, context={'request': request, 'icompanyid': icompanyid,'id': id})

        if series_serializer.is_valid():
            try:
                with transaction.atomic():
                    # Needed data for itemwomaster
                    # new_woid = series_serializer.save()
                    instance = series_serializer.save()

                    new_woid = series_serializer.context.get('new_woid')
                    prefix = series_serializer.context.get('prefix')
                    current_docno = series_serializer.context.get('current_docno')
                    sufix = series_serializer.context.get('sufix')

                    docnotion = 24 # this will be set after march , generate accordingly

                    print(new_woid)
                    #End Item wo master

                    # Add the new_woid to the wo_master_data and wo_detail_data
                    data['wo_master_data']['icompanyid'] = icompanyid
                    data['wo_master_data']['woid'] = new_woid
                    data['wo_master_data']['sprefix'] = prefix
                    data['wo_master_data']['swono'] = current_docno
                    data['wo_master_data']['ssufix'] = sufix
                    data['wo_master_data']['docnotion'] = docnotion
                    data['wo_master_data']['isactive'] = 0

                    # data['wo_detail_data']['woid'] = docnotion
                    for index, detail in enumerate(data['wo_detail_data']):
                    # for detail in data['wo_detail_data']:
                        detail['woid'] = new_woid
                        detail['icompanyid'] = icompanyid
                        detail['jobno'] =  str(new_woid) + "-"+ str(index + 1)
                        detail['docnotion'] = docnotion
                        detail['isactive'] = 0
                        for del_address in detail['del_address']:
                            del_address['woid'] = new_woid
                            del_address['jobno'] = index + 1
                            del_address['docnotion'] = docnotion
                            del_address['icompanyid'] = icompanyid

                    # Save the item_womaster data
                    wo_master_data = data['wo_master_data']
                    print(wo_master_data)
                    
                    wo_master_serializer = WOMasterSerializer(data=wo_master_data)
                    if wo_master_serializer.is_valid():
                        wo_master_serializer.save()
                    else:
                        raise serializers.ValidationError(wo_master_serializer.errors)

                    # Save the item_wodetail data
                    for detail in data['wo_detail_data']:
                        wo_detail_serializer = WODetailSerializer(data=detail)
                        if wo_detail_serializer.is_valid():
                            wo_detail_serializer.save()
                        else:
                            raise serializers.ValidationError(wo_detail_serializer.errors)

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
                'txt_woid': openapi.Schema(type=openapi.TYPE_STRING, description='Search by Work Order ID (partial match)'),
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
        tags=['Order Management / Workorder']
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
        woid = data.get('txt_woid', None)
        if woid:
            filters += f" AND a.woid LIKE '%{woid}%'"

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
            SELECT a.WOID, MAX(date_format(a.WODate, '%d/%m/%Y')) AS WODate, a.WONo, Get_CompanyName(a.ClientId) AS CompanyName
            FROM item_womaster AS a
            JOIN item_wodetail AS b ON a.woid = b.woid
            JOIN item_fpmasterext AS d ON b.ItemID = d.ProductID
            WHERE 1=1 {filters}
            GROUP BY b.WOId, a.WONo
            ORDER BY a.WODate DESC {limitQ};
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            response_data = {
                "message": "Success",
                "data": {
                    "wo_list": result,
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
                'woid': openapi.Schema(type=openapi.TYPE_STRING, description='Work Order ID'),
            },
            required=['woid']
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
        tags=['Order Management / Workorder']
    )
    def post(self, request, format=None):
        woid = request.data.get('woid', None)
        
        if not woid:
            return Response(
                {"error": True, "message": "woid parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        query = """
            SELECT a.WOId, a.JobNo, b.Description, b.AccCode, b.IPrefix
            FROM item_wodetail as a
            JOIN item_fpmasterext as b ON a.ItemID = b.ProductID
            WHERE a.woid = %s;
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, [woid])
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]

            response_data = {
                    "message": "Success",
                    "data": {
                        "wo_data": result,
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
        operation_summary="Retrieve Work Order Data",
        operation_description="Fetch data from ItemWodetail, ItemWomaster, and Companydelqtydate tables using woid and icompanyid.",
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
                'icompanyid': openapi.Schema(type=openapi.TYPE_STRING, description='ICompany ID'),
            },
            required=['woid', 'icompanyid']
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
                                'wo_data': openapi.Schema(type=openapi.TYPE_OBJECT)
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description='Bad request'),
            401: openapi.Response(description='Unauthorized'),
            500: openapi.Response(description='Internal server error')
        },
        tags=['Order Management / Workorder']
    )
    def post(self, request, format=None):
        woid = request.data.get('woid')
        icompanyid = request.data.get('icompanyid')

        if not woid or not icompanyid:
            return Response(
                {"error": True, "message": "woid and icompanyid parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item_wodetail_qs = ItemWodetail.objects.filter(woid=woid, icompanyid=icompanyid)
            item_womaster_qs = ItemWomaster.objects.filter(woid=woid, icompanyid=icompanyid)
            companydelqtydate_qs = Companydelqtydate.objects.filter(woid=woid, icompanyid=icompanyid)

            item_wodetail_serializer = ItemWodetailSerializer(item_wodetail_qs, many=True)
            item_womaster_serializer = ItemWomasterSerializer(item_womaster_qs, many=True)
            companydelqtydate_serializer = CompanydelqtydateSerializer(companydelqtydate_qs, many=True)

            result = {
                "item_wodetail": item_wodetail_serializer.data,
                "item_womaster": item_womaster_serializer.data,
                "companydelqtydate": companydelqtydate_serializer.data,
            }

            response_data = {
                "message": "Success",
                "data": {
                    "wo_data": result,
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
        tags=['Order Management / Workorder']
    )
    def get(self, request, format=None):
        try:
            user = GetUserData.get_user(request)
            icompanyid = user.icompanyid

            companies = Companymaster.objects.filter(companyid=icompanyid, isactive=True).order_by('companyname')
            companies_results = CompanySerializer(companies, many=True).data

            response_data = {
                "message": "Success",
                "data": {
                    "companies": companies_results,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": "Internal Server Error", "errorMessage": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# End Order Management Section 