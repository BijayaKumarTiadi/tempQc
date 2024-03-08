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

#PRivate methods

from .encodedDbs import encode_string



class CustomUserLoginView(APIView):#user authentication using 1 method
    serializer_class = CustomUserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LoginApi(APIView):#user authentication using 2 method whichh needs encrypted password for security
    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)
            
            if serializer.is_valid():
                userloginname = serializer.validated_data['userloginname']
                password = serializer.validated_data['password']
                IcompanyID = serializer.validated_data['IcompanyID']
                db_encode = serializer.validated_data['db_encode']
                print(userloginname,password)
                # Use 'userloginname' instead of 'username' in authenticate
                user = authenticate(request, userloginname=userloginname, password=password)
                
                if user is None:
                    return Response({'status': 400, 'message': 'Invalid Password', 'data': {}})
                else:
                    refresh = RefreshToken.for_user(user)
                    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})

            return Response({'status': 400, 'message': 'Something went wrong', 'data': serializer.errors})
        except Exception as e:
            print(e)
    def get(self, request):
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




def apipage(request):
    friends=['API Accounts Server Running ...']
    return JsonResponse(friends,safe=False)


