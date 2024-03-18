from django.shortcuts import render

from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import  LoginSerializer
from django.contrib.auth import authenticate
from django.db import connection, connections
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from rest_framework import status

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
#Private methods

from .encodedDbs import encode_string,decode_string



class GetIcompanyId(APIView):
    """
    API endpoint to retrieve company names and IDs.

    This endpoint dynamically switches the database connection based on the provided database name,
    retrieves the company names and IDs from the 'companyprofile' table, and returns the data.

    Parameters:
        - db_encode (str): The encoded database name.

    Returns:
        - company_profile (list of dict): List of dictionaries containing company names and IDs.
    """
    @swagger_auto_schema(
        operation_summary="Retrieve company names and IDs",
        operation_description="This endpoint retrieves company names and IDs from the 'companyprofile' table.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'db_encode': openapi.Schema(type=openapi.TYPE_STRING, description="Encoded database name"),
            },
            required=['db_encode']
        ),
        responses={
            200: "Successful retrieval of company names and IDs",
            500: "Internal server error"
        }
    )
    def post(self, request):
        data = request.data
        dbname=decode_string(str(data.get('db_encode')))
        connection.settings_dict['NAME'] = dbname
        """
        dbname=decode_string(str(db_encode))
        for db_key, db_config in connections.databases.items():
            if db_config['NAME'] == dbname:
                dbname = db_key
                break

        # Now use it ...
        #  
        if dbname:
            # Dynamically switch the database connection
            with connections[dbname].cursor() as cursor:
                cursor.execute(f"USE {dbname};")
        """
        try:
            if dbname:
                with connection.cursor() as cursor:
                    cursor.execute("""SELECT CompanyName,IcompanyID FROM companyprofile;""")
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()

                    # data = {
                    #     'company_profile': [dict(zip(columns, row)) for row in results]
                    # }
                    company_profile = [dict(zip(columns, row)) for row in results]
                    return Response({"message": "Success","data": {"company_profile": company_profile}},status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Failed to retrieve company names and IDs: {str(e)}"
            raise APIException(detail=error_message, code=500)



class LoginApi(APIView):#user authentication using 2 method whichh needs encrypted password for security
    """
        LoginApi

        This API view handles user authentication using encrypted passwords.
        The authentication process is validated in the associated serializer for code clarity.
        
        Methods:
        - POST: Authenticates the user using the provided credentials.
        - GET: Fetches financial year details and company profiles.

        Usage:
        - Use POST with userloginname, password, icompanyid, and db_encode to authenticate.
        - Use GET to retrieve financial year details and company profiles.

        Serializer:
        - LoginSerializer: Validates user authentication credentials.

        Raises:
        - APIException: Raised for unexpected errors during GET request.

        Note:
        - The financial year details and company profiles are fetched using a custom database query.
        - Ensure the correct user authentication and company ID before accessing the GET endpoint.
    """
    @swagger_auto_schema(
        operation_summary="Authenticate user",
        operation_description="Authenticates the user using the provided credentials.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'userloginname': openapi.Schema(type=openapi.TYPE_STRING, description="User login name"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="User password"),
                'icompanyid': openapi.Schema(type=openapi.TYPE_STRING, description="Company ID"),
                'db_encode': openapi.Schema(type=openapi.TYPE_STRING, description="Encoded database name"),
            },
            required=['userloginname', 'password', 'icompanyid', 'db_encode']
        ),
        responses={
            200: "Authentication successful",
            400: "Invalid user or password",
            500: "Internal server error"
        }
    )
    def post(self, request):
        """
            POST Method

            Authenticates the user using the provided credentials.

            Parameters:
            - userloginname (str): User login name.
            - password (str): User password.
            - icompanyid (str): Company ID associated with the user.
            - db_encode (str): Encoded database name.

            Returns:
            - Response: Authenticated user details with access and refresh tokens.
        """
        try:
            data = request.data
            serializer = LoginSerializer(data=data)
            
            if serializer.is_valid():
                userloginname = serializer.validated_data['userloginname']
                password = serializer.validated_data['password']
                icompanyid = serializer.validated_data['icompanyid']
                db_encode = serializer.validated_data['db_encode']
                # Use 'userloginname' instead of 'username' in authenticate 
                # if you want to use icompanyid then you need to configure the custome authentication function , for now this is only accepts useloginname and password with added user.icompanyid
                # You can decode the db_encode here -->
                """
                #Get the database names according to the user selects
                dbname=decode_string(str(db_encode))
                for db_key, db_config in connections.databases.items():
                    if db_config['NAME'] == dbname:
                        dbname = db_key
                        break
                # Now use it ... 
                if dbname:
                    # Dynamically switch the database connection
                    with connections[dbname].cursor() as cursor:
                        cursor.execute(f"USE {dbname};")
                """
                dbname=decode_string(str(db_encode))
                connection.settings_dict['NAME'] = dbname
                user = authenticate(request, userloginname=userloginname, password=password)
                
                if user is None:
                    return Response({'message': 'Invalid User or Password', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if user.icompanyid == icompanyid:
                        refresh = RefreshToken.for_user(user)
                        return Response({'refresh': str(refresh), 'access': str(refresh.access_token), "message": "Success", "data":{"userloginname":userloginname}},status=status.HTTP_200_OK)
                    else:
                        return Response({'message': 'icompanyid not matched ...', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Something went wrong', 'data': serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = f"Failed to Post login : {str(e)}"
            raise APIException(detail=error_message, code=500)
        

    @swagger_auto_schema(
        operation_summary="Fetch financial year details",
        operation_description="Retrieves financial year details and company profiles.",
        responses={
            200: "Success",
            500: "Internal server error"
        }
    )
    def get(self, request):
        """
            GET Method

            Fetches financial year details and company profiles.

            Returns:
            - Response: Financial year details and company profiles.
        """
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("""SELECT path, FinYear FROM admin.finyeardetails;SELECT CompanyName, IcompanyID FROM companyprofile;""")
                columns1 = [col[0] for col in cursor.description]
                results1 = cursor.fetchall()
                finyear_details = [{columns1[i]: encode_string(str(value)) if columns1[i] == 'path' else str(value) for i, value in enumerate(row)} for row in results1]
                return Response({
                    "message": "Success",
                    "data": {"finyear_details": finyear_details}
                },status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Something went wrong: {str(e)}"
            raise APIException(detail=error_message, code=status.HTTP_500_INTERNAL_SERVER_ERROR)




class GetDataView(APIView):
    """
    To test the JWT Token is actually working and the permission classes are working or not.
    This requires the authentication token provided by Django Simple JWT
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Test of JWT Auth",
        operation_description="response in message if the user is authenticated and send the Token with header.",
        responses={
            200: "Success",
            401: "Unauthorized",
            500: "Internal server error"
        }
    )
    def get(self, request):
        # Your logic to fetch data goes here
        data = {"message": "This is protected data"}
        return Response(data, status=status.HTTP_200_OK)

class Dashboard(APIView):
    """
        Dashboard View

        This view provides access to the dashboard for authenticated users.

        Authentication:
        - Requires JWT token authentication.

        Permissions:
        - Requires the user to be authenticated.

        Methods:
        - GET: Fetches user information for the authenticated user.

        Returns:
        - Response: A JSON response containing user information.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Fetch user information",
        operation_description="Retrieves user information for the authenticated user.",
        responses={
            200: "Success",
            401: "Unauthorized",
            500: "Internal server error"
        }
    )

    def get(self, request):
        """
        Get user information for the authenticated user.

        Returns:
            Response: A JSON response containing user information.
        """
        try:
            user = request.user
            userloginname=user.userloginname
            modules={"modules": 
                    [
                        "Quotation Management",
                        "Work Order",
                        "Stock Location",
                        "Order Management",
                        "Production Planning",
                        "Quality Control (QC)",
                        "Quality Assurance (QA)",
                        "Dispatch",
                        "Eway bill",
                        "Purchase",
                        "Inventory",
                        "Tallyposting",
                        "Prerequisites",
                        "Plate Management"
                    ]}
            
            return JsonResponse({"message": "Success", "data": modules}, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"Failed to fetch user information: {str(e)}"
            return JsonResponse({"statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def apipage(request):
    friends=['API Accounts Server Running ...']
    return JsonResponse(friends,safe=False)

