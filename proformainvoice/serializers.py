# serializers.py
from rest_framework import serializers
from django.db import transaction
# from .models import UploadedFile
from mastersapp.models import Employeemaster, ItemFpmasterext
from mastersapp.models import Companymaster
from mastersapp.models import Seriesmaster
from mastersapp.models import CompanymasterEx1
from proformainvoice.models import ItemWomaster
from mastersapp.models import Companydelqtydate
from mastersapp.models import ItemWodetail

from .models import Paymentterms
from .models import ItemSpec
from .models import Mypref
# class UploadedFileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UploadedFile
#         fields = ['pdf_file']



class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seriesmaster
        fields = ['id', 'prefix','isactive']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Companymaster
        fields = ['companyid', 'companyname']

class ExtendedCompanySerializer(CompanySerializer):
    isactive = serializers.IntegerField(read_only=True)

    class Meta(CompanySerializer.Meta):
        fields = CompanySerializer.Meta.fields + ['isactive']



class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employeemaster
        fields = ['empid', 'empname']

class PaymentTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paymentterms
        fields = ['payid', 'narration']

class CompanyEx1Serializer(serializers.ModelSerializer):
    class Meta:
        model = CompanymasterEx1
        fields = ['detailid', 'cname']


class ItemSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemSpec
        fields = '__all__'
        
class MyprefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mypref
        fields = ['mainheading','result','defultresult']



class SeriesMasterSaveSerializer(serializers.ModelSerializer):
    # If you use only serializers.serializer insted of modelserializer then you can use only a series_id
    class Meta:
        model = Seriesmaster 
        fields = ['id']

    def create(self, validated_data):
        icompanyid = self.context['icompanyid']
        seriesid = self.context['id']

        if not icompanyid:
            raise serializers.ValidationError('Company ID is required')

        try:
            with transaction.atomic():
                # Transaction Handling :- > The view uses transaction.atomic to ensure that the operations are atomic. 
                # This prevents race conditions when multiple requests try to update the Seriesmaster table simultaneously.
                series = Seriesmaster.objects.select_for_update().get(
                    doctype='Work Order',
                    id = seriesid,
                    isactive=1,
                    icompanyid=icompanyid
                )
                current_docno = int(series.docno)
                # new_woid = f"{series.prefix}{current_docno:03d}{series.sufix}" # For 3 digit
                new_woid = f"{series.prefix}/{current_docno}{series.sufix}"
                series.docno = str(current_docno + 1)
                series.save()
                # return new_woid,series.prefix,current_docno,series.sufix
                self.context['new_woid'] = new_woid
                self.context['prefix'] = series.prefix
                self.context['current_docno'] = current_docno
                self.context['sufix'] = series.sufix

                return series

        except Seriesmaster.DoesNotExist:
            raise serializers.ValidationError('Seriesmaster record not found')
        except Exception as e:
            raise serializers.ValidationError(str(e))
        


#This is auto require 
class WOMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemWomaster
        fields = [
            'woid', 'sprefix', 'swono', 'ssufix', 'icompanyid', 'wodate', 'clientid',
            'postatus', 'wono', 'podate', 'execid', 'orderedby', 'paymentday', 'paymenttype',
            'filelocation', 'remarks', 'proofingchk','poreceivedate','docnotion','isactive'
        ]
        extra_kwargs = {field: {'required': False} for field in fields}

class CompanyDelQtyDateSerializer(serializers.ModelSerializer):
    qtytodeliver = serializers.IntegerField(required=False, default=0)
    class Meta:
        model = Companydelqtydate
        fields = [
        'woid', 'recordid_old', 'jobno', 'icompanyid', 'clientid', 'delrecordid', 'billingrecordid',
        'schdeliverydate', 'lastdeliverydate', 'qtytodeliver','qtydelivered', 'specid', 'itemid', 'docnotion']
        extra_kwargs = {field: {'required': False} for field in fields} 


class WODetailSerializer(serializers.ModelSerializer):
    artworkno = serializers.CharField(required=False, allow_blank=True)
    freight = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    class Meta:
        model = ItemWodetail
        fields = [
        'woid', 'jobno', 'icompanyid', 'itemdesc', 'itemcode', 'codeno', 'itemid', 'quantity', 'qtyplus',
        'qtyminus', 'rate', 'actualrate', 'unitid', 'rateinthousand', 'rateunit', 'artworkno',
        'amount', 'percentvar', 'freight', 'specification', 'ref', 'color', 'cp', 'docnotion',
        'remarks', 'transfer_wo', 'hold', 'dontshowforjc', 'artworkreceive', 'closedate', 'templateid','isactive']
        extra_kwargs = {field: {'required': False} for field in fields}

    def create(self, validated_data):
        item_wodetail = ItemWodetail.objects.create(**validated_data)
        return item_wodetail


"""
#With some extra feature
class WOMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemWomaster
        fields = [
            'woid', 'sprefix', 'swono', 'ssufix', 'icompanyid', 'wodate', 'clientid',
            'postatus', 'wono', 'podate', 'execid', 'orderedby', 'paymentday', 'paymenttype',
            'filelocation', 'remarks', 'proofingchk', 'poreceivedate', 'docnotion', 'isactive'
        ]
        extra_kwargs = {
            'sprefix': {'required': False, 'allow_null': True},
            'swono': {'required': False, 'allow_null': True},
            'ssufix': {'required': False, 'allow_null': True},
            'wodate': {'required': False, 'allow_null': True},
            'clientid': {'required': False, 'allow_null': True},
            'postatus': {'required': False, 'allow_null': True},
            'wono': {'required': False, 'allow_null': True},
            'podate': {'required': False, 'allow_null': True},
            'execid': {'required': False, 'allow_null': True},
            'orderedby': {'required': False, 'allow_null': True},
            'paymentday': {'required': False, 'allow_null': True},
            'paymenttype': {'required': False, 'allow_null': True},
            'filelocation': {'required': False, 'allow_null': True},
            'remarks': {'required': False, 'allow_null': True},
            'proofingchk': {'required': False, 'allow_null': True},
            'poreceivedate': {'required': False, 'allow_null': True},
            'docnotion': {'required': False, 'allow_null': True},
            'isactive': {'required': False, 'allow_null': True},
        }

class CompanyDelQtyDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companydelqtydate
        fields = [
            'woid', 'recordid_old', 'jobno', 'icompanyid', 'clientid', 'delrecordid', 'billingrecordid',
            'schdeliverydate', 'lastdeliverydate', 'qtytodeliver', 'qtydelivered', 'specid', 'itemid', 'docnotion'
        ]
        extra_kwargs = {
            'recordid_old': {'required': False, 'allow_null': True},
            'jobno': {'required': False, 'allow_null': True},
            'icompanyid': {'required': False, 'allow_null': True},
            'clientid': {'required': False, 'allow_null': True},
            'delrecordid': {'required': False, 'allow_null': True},
            'billingrecordid': {'required': False, 'allow_null': True},
            'schdeliverydate': {'required': False, 'allow_null': True},
            'lastdeliverydate': {'required': False, 'allow_null': True},
            'qtytodeliver': {'required': False, 'allow_null': True},
            'qtydelivered': {'required': False, 'allow_null': True},
            'specid': {'required': False, 'allow_null': True},
            'itemid': {'required': False, 'allow_null': True},
            'docnotion': {'required': False, 'allow_null': True},
        }

class WODetailSerializer(serializers.ModelSerializer):
    del_address = CompanyDelQtyDateSerializer(many=True, required=False)

    class Meta:
        model = ItemWodetail
        fields = [
            'woid', 'jobno', 'icompanyid', 'itemdesc', 'itemcode', 'codeno', 'itemid', 'quantity', 'qtyplus',
            'qtyminus', 'rate', 'actualrate', 'unitid', 'rateinthousand', 'rateunit', 'artworkno',
            'amount', 'percentvar', 'freight', 'specification', 'ref', 'color', 'cp', 'docnotion',
            'remarks', 'transfer_wo', 'hold', 'dontshowforjc', 'artworkreceive', 'closedate', 'templateid', 'isactive', 'del_address'
        ]
        extra_kwargs = {
            'jobno': {'required': False, 'allow_null': True},
            'icompanyid': {'required': False, 'allow_null': True},
            'itemdesc': {'required': False, 'allow_null': True},
            'itemcode': {'required': False, 'allow_null': True},
            'codeno': {'required': False, 'allow_null': True},
            'itemid': {'required': False, 'allow_null': True},
            'quantity': {'required': False, 'allow_null': True},
            'qtyplus': {'required': False, 'allow_null': True},
            'qtyminus': {'required': False, 'allow_null': True},
            'rate': {'required': False, 'allow_null': True},
            'actualrate': {'required': False, 'allow_null': True},
            'unitid': {'required': False, 'allow_null': True},
            'rateinthousand': {'required': False, 'allow_null': True},
            'rateunit': {'required': False, 'allow_null': True},
            'artworkno': {'required': False, 'allow_null': True},
            'amount': {'required': False, 'allow_null': True},
            'percentvar': {'required': False, 'allow_null': True},
            'freight': {'required': False, 'allow_null': True},
            'specification': {'required': False, 'allow_null': True},
            'ref': {'required': False, 'allow_null': True},
            'color': {'required': False, 'allow_null': True},
            'cp': {'required': False, 'allow_null': True},
            'docnotion': {'required': False, 'allow_null': True},
            'remarks': {'required': False, 'allow_null': True},
            'transfer_wo': {'required': False, 'allow_null': True},
            'hold': {'required': False, 'allow_null': True},
            'dontshowforjc': {'required': False, 'allow_null': True},
            'artworkreceive': {'required': False, 'allow_null': True},
            'closedate': {'required': False, 'allow_null': True},
            'templateid': {'required': False, 'allow_null': True},
            'isactive': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        del_address_data = validated_data.pop('del_address', [])
        item_wodetail = ItemWodetail.objects.create(**validated_data)
        
        for del_address in del_address_data:
            del_address['woid'] = item_wodetail.woid
            Companydelqtydate.objects.create(**del_address)
        
        return item_wodetail
"""

class ItemFpmasterextSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFpmasterext
        fields = ['description', 'acccode', 'iprefix']

class ItemWodetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemWodetail
        fields = '__all__'
        # exlude = ['']

class ItemWomasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemWomaster
        fields = '__all__'

class CompanydelqtydateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companydelqtydate
        fields = '__all__'

'''
# YOu can use the below got get the fields as it is in the databse table column names .
# Use this unchanged .
# class CompanydelqtydateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Companydelqtydate
#         fields = '__all__'

#     def to_representation(self, instance):
#         """
#         Ths is for the addn of the column names as it is in the data table . Remove it if not required.
#         """
#         representation = super().to_representation(instance)
#         custom_representation = {self.Meta.model._meta.get_field(field).db_column: value for field, value in representation.items()}
#         return custom_representation

# class ItemWodetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ItemWodetail
#         fields = '__all__'

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         custom_representation = {self.Meta.model._meta.get_field(field).db_column: value for field, value in representation.items()}
        
#         # Adding del_address . bcs no field in the model for the del_adrs
#         del_address_qs = Companydelqtydate.objects.filter(woid=instance.woid, icompanyid=instance.icompanyid)
#         custom_representation['del_address'] = CompanydelqtydateSerializer(del_address_qs, many=True).data
        
#         return custom_representation

# class ItemWomasterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ItemWomaster
#         fields = '__all__'

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         custom_representation = {self.Meta.model._meta.get_field(field).db_column: value for field, value in representation.items()}
#         return custom_representation

'''