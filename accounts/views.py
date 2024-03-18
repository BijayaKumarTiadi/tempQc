from django.shortcuts import render

from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomUserLoginSerializer, CustomUserSerializer, LoginSerializer
from django.contrib.auth import authenticate
from django.db import connection, connections
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser,OTP
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
import sentry_sdk
from django.template.loader import render_to_string
import random
import re
import uuid
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
                # columns2 = [col[0] for col in cursor.description]
                # results2 = cursor.fetchall()
                data = {
                    # 'finyear_details': [{columns1[i]: encode_string(str(value)) for i, value in enumerate(row)} for row in results1],
                    'finyear_details': [{columns1[i]: encode_string(str(value)) if columns1[i] == 'path' else str(value) for i, value in enumerate(row)} for row in results1],
                    # 'company_profile': [{columns2[i]: str(value) for i, value in enumerate(row)} for row in results2]
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
                # cursor.nextset()
                # columns2 = [col[0] for col in cursor.description]
                # results2 = cursor.fetchall()
                data = {
                    # 'finyear_details': [{columns1[i]: encode_string(str(value)) for i, value in enumerate(row)} for row in results1],
                    'finyear_details': [{columns1[i]: encode_string(str(value)) if columns1[i] == 'path' else str(value) for i, value in enumerate(row)} for row in results1],
                    # 'company_profile': [{columns2[i]: str(value) for i, value in enumerate(row)} for row in results2]
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

class Dashboard(APIView):
    """
    Dashboard view accessible only to authenticated users.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get user information for the authenticated user.

        Returns:
            Response: A JSON response containing user information.
        """
        user = request.user

        try:
            user_data = CustomUser.objects.get(userloginname=user.userloginname)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist."}, status=404)
        serializer = CustomUserSerializer(user_data)
        
        return Response(serializer.data)


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
                    columns1 = [col[0] for col in cursor.description]
                    results1 = cursor.fetchall()

                    data = {
                        'company_profile': [dict(zip(columns1, row)) for row in results1]
                    }
                    return Response(data)
        except Exception as e:
            raise APIException(str(e))



def apipage(request):
    friends=['API Accounts Server Running ...']
    return JsonResponse(friends,safe=False)



class ForgotPasswordOTPView(APIView):
    """
    View to send the OTP For Forget Password via email and update it in the database.
    This endpoint allows you to send the latest OTP via email and update it in the database.

    :param email: Recipient's email address.
    """

    @swagger_auto_schema(
        operation_summary="OTP for forgot or reset password.",
        operation_description="OTP for forgot or reset password.",
        manual_parameters=[openapi.Parameter('email', openapi.IN_QUERY, description="Recipient's email address",
                                             type=openapi.TYPE_STRING)],
        responses={
            200: 'OTP sent successfully',
            400: 'Bad Request - Email is required or no OTP exists for the email',
            500: 'Internal Server Error - Failed to send OTP via email',
        }
    )
    @csrf_exempt
    def post(self, request, format=None):
        """
        Send the latest OTP via email and update it in the database.

        :param request: The HTTP request object.
        :param format: The format of the response (e.g., JSON).
        :return: Returns a success message if the latest OTP is sent and updated successfully.
                 Returns an error message if no OTP exists for the email or if any issues occur.
        """
        sentry_sdk.capture_message("ForgotPasswordOTPView")
        email = request.query_params.get('email')

        if not email:
            return Response({'error': 'Email ID is mandatory to be entered. Please enter the email ID.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the email exists in the User table
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'Email ID entered by you is not registered with us. Please contact our support team for assistance.'},
                status=status.HTTP_404_NOT_FOUND)

        try:
            otp = OTP.objects.filter(
                email=email, expired=False).latest('created_at')
        except OTP.DoesNotExist:
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            otp = OTP(email=email, code=otp_code)
        # Generate a new 6-digit OTP
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        subject = 'OTP to Reset Password'
        message = render_to_string('settingapp_forgotpassword_otp.html',
                                   {'otp_code': otp_code, 'first_name': user.first_name.capitalize(),
                                    'last_name': user.last_name.capitalize()})

        try:
            # zeptomail_send_email(subject, content=message, from_email="", to_email=[email])

            otp.code = otp_code
            otp.save()
            return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            error_message = f"Failed to send the OTP via email. Please try after sometime."
            return Response({'error': error_message}, status=status.HTTP_429_TOO_MANY_REQUESTS)


class VerifyForgotPasswordOTPView(APIView):
    """
    View to verify the OTP code for password reset.

    This endpoint allows you to verify the OTP code provided by the user for password reset.
    If the OTP is valid and not expired, it is marked as expired, and the verification is successful.

    :param email: The user's email for which OTP is being verified.
    :param otp_code: The OTP code provided by the user.
    """

    @swagger_auto_schema(
        operation_summary="Verify the Forget/Reset Password OTP Code.",
        operation_description="Verify the Forget/Reset Password OTP Code.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
                'otp_code': openapi.Schema(type=openapi.TYPE_STRING, description="OTP code"),
            },
            required=['email', 'otp_code']
        ),
        responses={
            200: 'OTP verification successful',
            400: 'Invalid OTP code or OTP has expired',
        }
    )
    @csrf_exempt
    def post(self, request, format=None):
        """
        Verify the OTP code provided by the user for password reset.

        :param request: The HTTP request object.
        :param format: The format of the response (e.g., JSON).
        :return: Returns a success message if OTP verification is successful.
                 Returns an error message if the OTP is invalid or has expired.
        """
        sentry_sdk.capture_message("VerifyForgotPasswordOTPView")
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        if not email:
            return Response({'error': 'Email ID is mandatory to be entered. Please enter the email ID.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not otp_code:
            return Response({'error': 'OTP is mandatory to be entered. Please enter the OTP.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'Email ID entered by you is not registered with us. Please contact our support team for assistance.'},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            otp = OTP.objects.get(email=email, code=otp_code, expired=False)
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP. Please enter a valid OTP sent to your email.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if otp.is_expired():
            return Response({'error': 'OTP has expired. Please use Resend OTP to send a new OTP.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # OTP is valid
        otp.expired = True
        otp.save()
        token = RefreshToken.for_user(user)

        return Response(
            {'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'token': token,
             'msg': 'OTP verification successful'},
            status=status.HTTP_200_OK)
        




