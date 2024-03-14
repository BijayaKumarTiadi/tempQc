# yourapp/serializers.py
from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import connections

#Private imports
from .encodedDbs import decode_string

class CustomUserLoginSerializer(serializers.Serializer):
    """
        # you can also use this with custom authenication which including the icompanyid directly in the auth function but this will significanly increase the code size .
        class CustomBackend(ModelBackend):
        
        #Custom authentication backend to support icompanyid during login.
        def authenticate(self, request, userloginname=None, password=None, icompanyid=None, **kwargs):
            user = super().authenticate(request, username=userloginname, password=password, **kwargs)

            # Check additional conditions (icompanyid, etc.)
            if user and user.icompanyid != icompanyid:
                return None

            return user


        class CustomUserLoginSerializer(serializers.Serializer):
            userloginname = serializers.CharField()
            password = serializers.CharField()
            icompanyid = serializers.CharField()

            def validate(self, data):
                userloginname = data.get('userloginname')
                password = data.get('password')
                icompanyid = data.get('icompanyid')

                # Validate userloginname, password, and icompanyid
                user = authenticate(
                    request=self.context.get('request'),
                    userloginname=userloginname,
                    password=password,
                    icompanyid=icompanyid
                )

                if user:
                    refresh = RefreshToken.for_user(user)
                    data['refresh'] = str(refresh)
                    data['token'] = str(refresh.access_token)
                    return data
                else:
                    raise serializers.ValidationError('Invalid credentials...')
    """
    userloginname = serializers.CharField()
    password = serializers.CharField()
    icompanyid= serializers.CharField()
    db_encode = serializers.CharField()
    def validate(self, data):
        userloginname = data.get('userloginname')
        password = data.get('password')
        icompanyid = data.get('icompanyid')
        db_encode = data.get('db_encode')# Use it where necessary 
        # Decode the database name here -->
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
        # Validate userloginname and password
        # user = CustomUser.objects.filter(userloginname=userloginname, password=password).first()
        user = authenticate(request=self.context.get('request'), userloginname=userloginname, password=password)
        # print(user)
        if user:
            if user and user.icompanyid == icompanyid:
                refresh = RefreshToken.for_user(user)
                data['refresh'] = str(refresh)
                data['token'] = str(refresh.access_token)
                # return { 'refresh': str(refresh),'access': str(refresh.access_token),} # this only returns the tokens 
                return data
            else:
                raise serializers.ValidationError('Invalid icompanyid...')
        else:
            raise serializers.ValidationError('Invalid credentials...')

class LoginSerializer(serializers.Serializer):
    userloginname = serializers.CharField()
    password = serializers.CharField()
    icompanyid = serializers.CharField()
    db_encode = serializers.CharField()

    # username = request.data.get('username')
    # password = request.data.get('password')
    # IcompanyID = request.data.get('IcompanyID')
    # db_encode = request.data.get('db_encode')

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Using this serializer for the serialization of the User data which is fetched after login of the user.
    -> we can add the table of permissions here and do some permission stuff here .
    """
    class Meta:
        model = CustomUser
        # fields = ['id', 'userloginname', 'email']
        fields = '__all__'