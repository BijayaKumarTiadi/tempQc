# yourapp/serializers.py
from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

class CustomUserLoginSerializer(serializers.Serializer):
    userloginname = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        userloginname = data.get('userloginname')
        password = data.get('password')

        # Validate userloginname and password
        user = CustomUser.objects.filter(userloginname=userloginname, password=password).first()

        if user:
            refresh = RefreshToken.for_user(user)
            data['refresh'] = str(refresh)
            data['token'] = str(refresh.access_token)
            # return { 'refresh': str(refresh),'access': str(refresh.access_token),} # this only returns the tokens 
            return data
        else:
            raise serializers.ValidationError('Invalid credentials')

class LoginSerializer(serializers.Serializer):
    userloginname = serializers.CharField()
    password = serializers.CharField()
    IcompanyID = serializers.CharField()
    db_encode = serializers.CharField()

    # username = request.data.get('username')
    # password = request.data.get('password')
    # IcompanyID = request.data.get('IcompanyID')
    # db_encode = request.data.get('db_encode')