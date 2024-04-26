from rest_framework import serializers
from django.db import connection
from .models import EstItemtypemaster, EstItemtypedetail, Papermasterfull
from .models import  EstProcessInputDetail
from .models import  FrontendResponse
from .models import  EstAdvanceInputDetail,Companymaster
from .models import  Currencymaster
from .models import  Employeemaster
from .models import  EstNewQuote
from .models import PaperGridQty

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
    
class PaperGridQtySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperGridQty
        fields = (
            'Inc', 'Dackle_Dim', 'Grain_Dim', 'Ups', 'AreaPerCarton_SqInch',
            'Scan', 'Grain', 'MachineID', 'MachineName', 'NoOfPass_req', 'Mat_X',
            'Mat_Y', 'DieLength_In_Inch', 'Qty', 'F_Color', 'B_Color',
            'Die_PlanHeight', 'Die_PlanWidth', 'FullSheet_D', 'FullSheet_G',
            'FullSheet_Grain', 'FullSheet_Cut_X', 'FullSheet_Cut_Y', 'FullSheet_Ups',
            'Sheets_A', 'HeightCut', 'WidthCut', 'LengthRemaining', 'WidthRemaining',
            'ItemsInFirstCut', 'TotalCuts', 'TotalBox', 'Dackle_Dim_B', 'Grain_Dim_B',
            'Ups_B', 'Mat_X_B', 'Mat_Y_B', 'Cuts_B', 'Sheets_B', 'Dackle_Dim_C',
            'Grain_Dim_C', 'Ups_C', 'Mat_X_C', 'Mat_Y_C', 'Cuts_C', 'Sheets_C',
            'Dackle_Dim_D', 'Grain_Dim_D', 'Ups_D', 'Mat_X_D', 'Mat_Y_D', 'Cuts_D',
            'Sheets_D', 'Dackle_Dim_Tot', 'Grain_Dim_Tot', 'Wastage_X', 'Wastage_Y',
            'Wastage_Weight_kg_A', 'Wastage_Weight_kg_B', 'Wastage_Weight_kg',
            'UtilizationPer', 'FullSheet_Req', 'PaperID', 'Gsm', 'Paper_Rate',
            'Paper_Unit', 'Print_Size_Sheets', 'Print_Impression', 'Paper_Kg',
            'Paper_Kg_FullSheet', 'Paper_Amt', 'PunchDie_Amt', 'Plate_Amt',
            'PrMake_Ready_Amt', 'Printing_Amt', 'Total_Amt', 'PN_McID',
            'PN_MachineName', 'PN_MaxDackle', 'PN_MinDackle', 'PN_MaxGrain',
            'PN_MinGrain', 'PN_Gripper', 'PN_MakeRdy_Amt', 'PN_Punching_Amt'
        )