from rest_framework import serializers
from .models import EstItemtypemaster, EstItemtypedetail, Papermasterfull
from .models import  EstProcessInputDetail

class EstItemtypedetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstItemtypedetail
        fields = ['label_name', 'default_value']

class EstItemtypemasterSerializer(serializers.ModelSerializer):
    itemtypedetail_set = EstItemtypedetailSerializer(many=True, read_only=True)
    #You can enable this and add the var in the fields to get the itemtype details in the api response 
    
    class Meta:
        model = EstItemtypemaster
        fields = ['id', 'internalCartonType', 'CartonType', 'ecma_code', 'imgpath','hover_imgpath','itemtypedetail_set']




class PaperMasterFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Papermasterfull
        fields = '__all__'



class InputDetailSerializer(serializers.ModelSerializer):
    dropdown_list = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = EstProcessInputDetail 
        # fields = '__all__'
        fields = ['id', 'prid', 'sp_process_no', 'input_label_name', 'input_type', 'input_data_type', 'input_default_value', 'seqno', 'isactive', 'dropdown_list']
