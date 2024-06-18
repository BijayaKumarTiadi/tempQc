# serializers.py
from rest_framework import serializers
# from .models import UploadedFile
from mastersapp.models import Employeemaster
from mastersapp.models import Companymaster
from mastersapp.models import Seriesmaster
from mastersapp.models import CompanymasterEx1
from .models import Paymentterms
# class UploadedFileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UploadedFile
#         fields = ['pdf_file']



class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seriesmaster
        fields = ['id', 'prefix']

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