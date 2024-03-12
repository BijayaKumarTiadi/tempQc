from django.shortcuts import render

from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomUserLoginSerializer, LoginSerializer
from django.contrib.auth import authenticate
from django.db import connection, connections
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

#Private methods

from .encodedDbs import encode_string,decode_string



class CustomUserLoginView(APIView):#user authentication using 1 method
    """
        CustomUserLoginView

        This view handles user authentication using the provided credentials.
        The authentication process is validated in the associated serializer for code clarity.

        Methods:
        - POST: Authenticates the user using the provided credentials.
        - GET: Fetches financial year details and company profiles.

        Usage:
        - Use POST with userloginname and password to authenticate.
        - Use GET to retrieve financial year details and company profiles.

        Serializer:
        - CustomUserLoginSerializer: Validates user authentication credentials.

        Raises:
        - APIException: Raised for unexpected errors during GET request.

        Note:
        - The financial year details and company profiles are fetched using a custom database query.
        - Use appropriate API authentication before accessing these endpoints.
    """
    serializer_class = CustomUserLoginSerializer

    def post(self, request):
        """
            POST Method

            Authenticates the user using the provided credentials.

            Parameters:
            - userloginname (str): User login name.
            - password (str): User password.

            Returns:
            - Response: Authenticated user details with access and refresh tokens.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
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
                cursor.nextset()
                columns2 = [col[0] for col in cursor.description]
                results2 = cursor.fetchall()
                data = {
                    # 'finyear_details': [{columns1[i]: encode_string(str(value)) for i, value in enumerate(row)} for row in results1],
                    'finyear_details': [{columns1[i]: encode_string(str(value)) if columns1[i] == 'path' else str(value) for i, value in enumerate(row)} for row in results1],
                    'company_profile': [{columns2[i]: str(value) for i, value in enumerate(row)} for row in results2]
                    # 'company_profile': [dict(zip(columns2, row)) for row in results2]
                }
                return Response(data)
        except Exception as e:
            raise APIException('Something went wrong!')

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
                user = authenticate(request, userloginname=userloginname, password=password)
                
                if user is None:
                    return Response({'status': 400, 'message': 'Invalid Password', 'data': {}})
                else:
                    if user.icompanyid == icompanyid:
                        refresh = RefreshToken.for_user(user)
                        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
                    else:
                        return Response({'status': 400, 'message': 'icompanyid not matched ...', 'data': serializer.errors})
            return Response({'status': 400, 'message': 'Something went wrong', 'data': serializer.errors})
        except Exception as e:
            print(e)
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
                cursor.nextset()
                columns2 = [col[0] for col in cursor.description]
                results2 = cursor.fetchall()
                data = {
                    # 'finyear_details': [{columns1[i]: encode_string(str(value)) for i, value in enumerate(row)} for row in results1],
                    'finyear_details': [{columns1[i]: encode_string(str(value)) if columns1[i] == 'path' else str(value) for i, value in enumerate(row)} for row in results1],
                    'company_profile': [{columns2[i]: str(value) for i, value in enumerate(row)} for row in results2]
                    # 'company_profile': [dict(zip(columns2, row)) for row in results2]
                }
                return Response(data)
        except Exception as e:
            raise APIException('Something went wrong!')





class GetDataView(APIView):
    """
    To test the JWT Token is actually working and the permission classes are working or not.
    This requires the authentication token provided by Django Simple JWT
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Your logic to fetch data goes here
        data = {"message": "This is protected data"}
        return Response(data)


def apipage(request):
    friends=['API Accounts Server Running ...']
    return JsonResponse(friends,safe=False)


