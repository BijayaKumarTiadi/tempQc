from rest_framework import serializers
from .models import EstItemtypemaster, EstItemtypedetail, Papermasterfull

class EstItemtypedetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstItemtypedetail
        fields = ['label_name', 'default_value']

class EstItemtypemasterSerializer(serializers.ModelSerializer):
    # itemtypedetail_set = EstItemtypedetailSerializer(many=True, read_only=True)
    #You can enable this and add the var in the fields to get the itemtype details in the api response 
    
    class Meta:
        model = EstItemtypemaster
        fields = ['id', 'internalCartonType', 'CartonType', 'ecma_code', 'imgpath','hover_imgpath']




class PaperMasterFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Papermasterfull
        fields = '__all__'