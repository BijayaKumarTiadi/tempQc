from rest_framework import serializers
from django.db import connection
from .models import EstItemtypemaster, EstItemtypedetail, Papermasterfull
from .models import  EstProcessInputDetail
from .models import  FrontendResponse
from .models import  EstAdvanceInputDetail

class EstItemtypedetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstItemtypedetail
        fields = ['label_name', 'default_value']

class EstItemtypemasterSerializer(serializers.ModelSerializer):
    itemtypedetail_set = EstItemtypedetailSerializer(many=True, read_only=True)
    #You can enable this and add the var in the fields to get the itemtype details in the api response 
    
    class Meta:
        model = EstItemtypemaster
        fields = ['id', 'internalCartonType', 'CartonType', 'ecma_code', 'imgpath','hover_imgpath','carton_cat','itemtypedetail_set']


class EstAdvanceInputDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstAdvanceInputDetail
        # fields = ['id', 'unique_name', 'input_label_name', 'input_type', 'input_data_type', 'input_default_value', 'seqno', 'isactive']
        fields = ['id', 'unique_name', 'input_label_name', 'input_type', 'input_data_type', 'input_default_value']

class PaperMasterFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Papermasterfull
        fields = '__all__'



class InputDetailSerializer(serializers.ModelSerializer):
    dropdown_list = serializers.ListField(child=serializers.DictField(), required=False)
    PrName = serializers.SerializerMethodField()
    class Meta:
        model = EstProcessInputDetail 
        # fields = '__all__'
        fields = ['id', 'prid', 'sp_process_no', 'input_label_name', 'input_type', 'input_data_type', 'input_default_value', 'seqno', 'isactive', 'dropdown_list','Unique_Name','PrName']
    def get_PrName(self, obj):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT PrName FROM item_processname AS a WHERE a.PrID = %s", [obj.prid])
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception:
            return None



# class FrontendResponseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FrontendResponse
#         fields = ['json_response', 'created_by', 'updated_by']
class FrontendResponseSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)

    class Meta:
        model = FrontendResponse
        fields = ['json_response', 'created_by', 'updated_by']



# Below serializer are for the input from the process input page , total 9 tables 
class ProcessInputSerializer(serializers.Serializer):
    # quoteid = serializers.IntegerField() like this if you want to add some optionl or required data
    grain_direction = serializers.CharField(max_length=1)
    board_details = serializers.ListField(child=serializers.DictField())
    quantity = serializers.ListField(child=serializers.IntegerField(min_value=0, required=True))

    def validate_grain_direction(self, value):
        """
        Validate grain direction field.
        """
        if value not in ['h', 'v']:
            raise serializers.ValidationError("Grain direction must be 'h' or 'v'.")
        return value
    def validate_board_details(self, value):
        """
        Validate board details field.
        """
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Board details must be a list of dictionaries.")

            required_keys = ['board_menufac', 'board_type', 'gsm'] # can add BoardID if its needed  .
            for key in required_keys:
                if key not in item:
                    raise serializers.ValidationError(f"Missing '{key}' in board details.")
        return value
    def validate_quantity(self, value):
        """
        Validate quantity field.
        """
        if not value:
            raise serializers.ValidationError("Quantity list cannot be empty.")
        return value