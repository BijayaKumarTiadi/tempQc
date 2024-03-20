from django.shortcuts import render

from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from .serializers import  LoginSerializer
from django.contrib.auth import authenticate
from django.db import connection, connections
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import AppModule,CustomUser,OTP
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
import sentry_sdk
from django.template.loader import render_to_string
import random
import re
from rest_framework import status
from accounts.utils.sendgrid_mail import *
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
import os
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from .permissions import ViewByStaffOnlyPermission
#Private methods

from .encodedDbs import encode_string,decode_string

SENDGRID_EMAIL = os.environ.get('SENDGRID_EMAIL')

        


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
        },
        tags=['Login to SmartMIS']
    )
    def post(self, request):
        data = request.data
        try:
            dbname=decode_string(str(data.get('db_encode')))
            connection.settings_dict['NAME'] = dbname
        except Exception as e:
            error_message = f"The Database Name Invalid : {str(e)}"
            return JsonResponse({ "error": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
            return JsonResponse({ "error": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        },
        tags=['Login to SmartMIS']
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
        },
        tags=['Login to SmartMIS']
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
            200: "Success",
            401: "Unauthorized",
            500: "Internal server error"
        },
        tags=['Login to SmartMIS']
    )
    def get(self, request):
        # Your logic to fetch data goes here
        data = {"message": "This is protected data"}
        return Response(data, status=status.HTTP_200_OK)


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
        },
        tags=['Login to SmartMIS']
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
                                   {'otp_code': otp_code, 'first_name': user.username.capitalize(),
                                    'last_name': user.username.capitalize()})

        try:
            sendgrid_send_mail(subject, content=message, from_email=SENDGRID_EMAIL, to_email=email)

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
        },
        tags=['Login to SmartMIS']
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
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token), "message": "OTP verification successful", "data":{'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email,"userloginname":user.userloginname}},status=status.HTTP_200_OK)

        

class UpdatePasswordView(APIView):
    """
    View to update a user's password.

    This endpoint allows you to update a user's password. The new password should meet complexity requirements
    and match the confirmation password.

    :param email: User's email.
    :param new_password: New password.
    :param confirm_new_password: Confirmation of the new password.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update User Password.",
        operation_description="Update User Password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
                'confirm_new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm new password')
            },
            required=['email', 'new_password', 'confirm_new_password']
        ),
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
            200: 'Password updated successfully',
            400: 'Password change failed: New password does not meet complexity requirements or passwords do not match.',
            401: 'Unauthorized: Invalid access token',
            404: 'Not Found.',
            500: 'Failed to reset the password. Please try again later.'
        },
        tags=['Login to SmartMIS']
    )
    @csrf_exempt
    def post(self, request, format=None):
        sentry_sdk.capture_message("UpdatePasswordView")
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email ID is mandatory to be entered. Please enter the email ID'},
                            status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')

        # Check if new password and confirm new password match
        if new_password != confirm_new_password:
            return Response({'error': 'Passwords do not match. Please recheck the passwords entered'},
                            status=status.HTTP_400_BAD_REQUEST)

        custom_password_validator = CustomPasswordValidator()

        try:
            # Use the custom password validator
            custom_password_validator.validate(new_password)
        except ValidationError as e:
            sentry_sdk.capture_exception(e)
            error_messages = ', '.join(e)
            return Response({'error': f'Password does not meet the strong password criteria. Please recheck the '
                                      f'criteria: {error_messages}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'Email ID entered by you is not registered with us. Please contact our support team for assistance.'},
                status=status.HTTP_404_NOT_FOUND)

        try:
            subject = 'Your password has been successfully reset'
            message = render_to_string('settingapp_reset_successful.html',
                                       {'first_name': user.first_name.capitalize(), 'last_name': user.last_name.capitalize()})
            
            sendgrid_send_mail(subject=subject, content=message, from_email=SENDGRID_EMAIL, to_email=[email])
            
            user.password = make_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            error_message = f"Failed to reset the password. Please try after sometime.. Exception: {str(e)}"
            return Response({'error': error_message}, status=status.HTTP_429_TOO_MANY_REQUESTS)



class CustomPasswordValidator:
    def __init__(self, min_length=12):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                "The password must be at least {} characters long.".format(self.min_length))
        if not any(char.isupper() for char in password):
            raise ValidationError(
                "The password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise ValidationError(
                "The password must contain at least one lowercase letter.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "The password must contain at least one special character.")

    def get_help_text(self):
        return ("Your password must be at least {} characters long and include at least one uppercase letter, "
                "one lowercase letter, and one special character.").format(
            self.min_length)

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
    # permission_classes = [IsAuthenticated]
    #This is the basic permission with the user master table ,  we can add more like that with customization
    permission_classes = [IsAuthenticated, ViewByStaffOnlyPermission]

    @swagger_auto_schema(
        operation_summary="Fetch user information",
        operation_description="Retrieves user information for the authenticated user.",
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
            200: "Success",
            401: "Unauthorized",
            500: "Internal server error"
        },
        tags=['Login to SmartMIS']
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
            # modules = AppModule.objects.filter(is_active=True)  # Filter out inactive modules
            # app_urls = {module.name: module.url for module in modules}
            modules = AppModule.objects.filter(is_active=True)
            # urls = [{'name': module.name, 'url': module.url} for module in modules]
            module_data = [{
                        'name': module.name,
                        'url': module.url,
                        'description': module.description,
                        'image_url': module.image.url if module.image else None,
                        'is_active': module.is_active,
                        'sort': module.sort
                    } for module in modules]
            
            return Response({"message": "Success","data": {"modules": module_data}},status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Failed to fetch user information: {str(e)}"
            return JsonResponse({"message": error_message, "data": {}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



        