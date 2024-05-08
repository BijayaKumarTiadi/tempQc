# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError


#import from helper
from .helper import pdf_processing
from .helper import gemini_1

#import from serializers
from .serializers import UploadedFileSerializer

import os
import json
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class PDFUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser]
    @swagger_auto_schema(
        operation_summary="Upload PDF and extract text",
        operation_description="Upload a PDF file and extract its text content.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True,
                format='Bearer <Token>'
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
        tags=['PDF Processing']
    )
    
    def post(self, request, format=None):
        try:
            serializer = UploadedFileSerializer(data=request.data)
            if serializer.is_valid():
                pdf_file = serializer.validated_data['pdf_file']
                pdf_text= pdf_processing(pdf_file)
                script_dir = os.path.dirname(__file__)
                json_file_path = os.path.join(script_dir, 'format.json')
                with open(json_file_path) as json_file:
                    company_formats = json.load(json_file)
                # The below field will be fetched from the frontend .
                sun_pharma_format = company_formats['company_formats']['SUN_PHARMACEUTICAL']
                data = gemini_1(pdf_text,sun_pharma_format).replace("'", '"')
                data = data.replace("None", 'null')
                parsed_data = json.loads(data)
                
                return Response({"message": "Data processed successfully", "data": parsed_data }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            error_message = "Invalid input data"
            return Response({"message": error_message, "errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = f"Failed to process pdfs : {str(e)}"
            return Response({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        