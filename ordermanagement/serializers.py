# serializers.py
from rest_framework import serializers
from django.db import transaction
# from .models import UploadedFile
from mastersapp.models import Employeemaster
from mastersapp.models import Companymaster
from mastersapp.models import Seriesmaster
from mastersapp.models import CompanymasterEx1
from mastersapp.models import ItemWomaster
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
        


class WOMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemWomaster
        fields = [
            'woid', 'sprefix', 'swono', 'ssufix', 'icompanyid', 'wodate', 'clientid',
            'postatus', 'wono', 'podate', 'execid', 'orderedby', 'paymentday', 'paymenttype',
            'filelocation', 'remarks', 'proofingchk','poreceivedate','docnotion','isactive'
        ]

class CompanyDelQtyDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companydelqtydate
        fields = [
        'woid', 'recordid_old', 'jobno', 'icompanyid', 'clientid', 'delrecordid', 'billingrecordid',
        'schdeliverydate', 'lastdeliverydate', 'qtytodeliver','qtydelivered', 'specid', 'itemid', 'docnotion']


class WODetailSerializer(serializers.ModelSerializer):
    del_address = CompanyDelQtyDateSerializer(many=True)
    class Meta:
        model = ItemWodetail
        fields = [
        'woid', 'jobno', 'icompanyid', 'itemdesc', 'itemcode', 'codeno', 'itemid', 'quantity', 'qtyplus',
        'qtyminus', 'rate', 'actualrate', 'unitid', 'rateinthousand', 'rateunit', 'artworkno',
        'amount', 'percentvar', 'freight', 'specification', 'ref', 'color', 'cp', 'docnotion',
        'remarks', 'transfer_wo', 'hold', 'dontshowforjc', 'artworkreceive', 'closedate', 'templateid','isactive', 'del_address']

    def create(self, validated_data):
        del_address_data = validated_data.pop('del_address', [])
        item_wodetail = ItemWodetail.objects.create(**validated_data)
        
        for del_address in del_address_data:
            del_address['woid'] = item_wodetail.woid
            Companydelqtydate.objects.create(**del_address)
        
        return item_wodetail

