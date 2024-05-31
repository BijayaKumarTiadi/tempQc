
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import json
from .models import ItemWomaster
from .utils import DataManager
from .helper import pdf_processing, gemini_1

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ValidationError


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

class Workorder(APIView):
    """
    API View to goto Dashboard.
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
        tags=['Order Management / Workorder']
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


# End Order Management Section 