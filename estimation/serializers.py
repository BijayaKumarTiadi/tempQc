from rest_framework import serializers
from .models import EstItemtypemaster, EstItemtypedetail

class EstItemtypedetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstItemtypedetail
        fields = ['label_name', 'default_value']

class EstItemtypemasterSerializer(serializers.ModelSerializer):
    itemtypedetail_set = EstItemtypedetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = EstItemtypemaster
        fields = ['id', 'internalCartonType', 'CartonType', 'ecma_code', 'imgpath', 'itemtypedetail_set']
