from rest_framework import serializers
from django.db import connection
from .models import EstItemtypemaster, EstItemtypedetail, Papermasterfull
from .models import  EstProcessInputDetail
from .models import  FrontendResponse
from .models import  EstAdvanceInputDetail,Companymaster
from .models import  Currencymaster
from .models import  Employeemaster
from .models import  EstNewQuote
from .models import PapergridQtyP

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.unique_name == "Client_Name_Drp":
            # Fetch all company names and IDs from the CompanyMaster model
            companies = Companymaster.objects.values('companyname', 'companyid')
            company_data = [{"label": company['companyname'], "value": company['companyid']} for company in companies]
            representation['select_options'] = company_data
        # You can use this if you want to only  add the Indian Rupees in the currency . * depends upon db .
        # elif instance.unique_name == "CurrancyID":
        #     # Fetch currency details from the Currencymaster model
        #     currency_instance = Currencymaster.objects.first()  # Assuming there is only one currency instance
        #     currency_details = {
        #         "CurrencyID": currency_instance.currencyid,
        #         "CurrencyName": currency_instance.currencyname,
        #         "CurrencySymbol": currency_instance.currencysymbol
        #     }
        #     representation['currency_details'] = currency_details
        elif instance.unique_name == "CurrancyID":
            currencies = Currencymaster.objects.all()
            currency_details = [
                {
                    "value": currency.currencyid,
                    "label": currency.currencyname,
                    "CurrencySymbol": currency.currencysymbol,
                    "is_default":currency.isdefault
                }
                for currency in currencies
            ]
            representation['select_options'] = currency_details
        elif instance.unique_name == "Our_Executive":
            Our_Executive = Employeemaster.objects.all()
            Our_Executive = [
                {
                    "value": Our_Executive.empid,
                    "label": Our_Executive.empname
                }
                for Our_Executive in Our_Executive
            ]
            representation['select_options'] = Our_Executive
        return representation
    class Meta:
        model = EstAdvanceInputDetail
        # fields = ['id', 'unique_name', 'input_label_name', 'input_type', 'input_data_type', 'input_default_value', 'seqno', 'isactive']
        fields = ['id', 'unique_name', 'input_label_name', 'input_type', 'input_data_type', 'input_default_value']
    #below methods is not used . If you want to use it , add the var at the top .
    # def get_company_id(self, obj):
    #     company_id = Companymaster.objects.values_list('companyid', flat=True)
    #     return company_id

    # def get_company_name(self, obj):
    #     company_name = Companymaster.objects.values_list('companyname', flat=True)
    #     return company_name

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
    dimensions = serializers.ListField(child=serializers.DictField())

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
    def validate_dimensions(self, value):
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Dimensions must be a list of dictionaries.")

            required_keys = ['label_name', 'value']
            for key in required_keys:
                if key not in item:
                    raise serializers.ValidationError(f"Missing '{key}' in dimensions.")
        return value
    

class EstNewQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstNewQuote
        fields = ['quotedate','quote_no','icompanyid','auid','clientid','client_name','product_name',
            'product_code','carton_type_id','adatetime','muid','mdatetime','remarks','orderstatus',
            'finalby','enqno','docnotion','estnotion','finaldate','repid','impexpstatus','revquoteno',
            'grainstyle','locationid','currencyid','currency_factctor','currency_curramt','clientcategoryid',
            'calculatedrate','quoterate','finalrate','fpid',]

    def save(self, **kwargs):
        """
        This is used for the log entry . 
        """
        request = kwargs.pop('request', None)
        instance = super().save(**kwargs)
        if request:
            instance.save(request=request)
        return instance
    
class PaperGridQtyPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PapergridQtyP
        fields = (
            'inc',
            'dackle_dim',
            'grain_dim',
            'ups',
            'areapercarton_sqinch',
            'scan',
            'grain',
            'machineid',
            'machinename',
            'noofpass_req',
            'mat_x',
            'mat_y',
            'dielength_in_inch',
            'qty',
            'f_color',
            'b_color',
            'die_planheight',
            'die_planwidth',
            'fullsheet_d',
            'fullsheet_g',
            'fullsheet_grain',
            'fullsheet_cut_x',
            'fullsheet_cut_y',
            'fullsheet_ups',
            'sheets_a',
            'heightcut',
            'widthcut',
            'lengthremaining',
            'widthremaining',
            'itemsinfirstcut',
            'totalcuts',
            'totalbox',
            'dackle_dim_b',
            'grain_dim_b',
            'ups_b',
            'mat_x_b',
            'mat_y_b',
            'cuts_b',
            'sheets_b',
            'dackle_dim_c',
            'grain_dim_c',
            'ups_c',
            'mat_x_c',
            'mat_y_c',
            'cuts_c',
            'sheets_c',
            'dackle_dim_d',
            'grain_dim_d',
            'ups_d',
            'mat_x_d',
            'mat_y_d',
            'cuts_d',
            'sheets_d',
            'dackle_dim_tot',
            'grain_dim_tot',
            'wastage_x',
            'wastage_y',
            'wastage_weight_kg_a',
            'wastage_weight_kg_b',
            'wastage_weight_kg',
            'utilizationper',
            'fullsheet_req',
            'paperid',
            'gsm',
            'paper_rate',
            'paper_unit',
            'print_size_sheets',
            'print_impression',
            'paper_kg',
            'paper_kg_fullsheet',
            'paper_amt',
            'punchdie_amt',
            'plate_amt',
            'prmake_ready_amt',
            'printing_amt',
            'total_amt',
            'pn_mcid',
            'pn_machinename',
            'pn_maxdackle',
            'pn_mindackle',
            'pn_maxgrain',
            'pn_mingrain',
            'pn_gripper',
            'pn_makerdy_amt',
            'pn_punching_amt',
        )