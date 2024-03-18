# yourapp/serializers.py
from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import connection, connections

#Private imports
from .encodedDbs import decode_string


class LoginSerializer(serializers.Serializer):
    userloginname = serializers.CharField()
    password = serializers.CharField()
    icompanyid = serializers.CharField()
    db_encode = serializers.CharField()

    # username = request.data.get('username')
    # password = request.data.get('password')
    # IcompanyID = request.data.get('IcompanyID')
    # db_encode = request.data.get('db_encode')

