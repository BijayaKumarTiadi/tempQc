# serializers.py
from rest_framework import serializers
from django.db import transaction
from mastersapp.models import Employeemaster
from mastersapp.models import Companymaster
from mastersapp.models import Seriesmaster
from mastersapp.models import CompanymasterEx1
from mastersapp.models import ItemWomaster
from mastersapp.models import Companydelqtydate
from mastersapp.models import ItemWodetail
from mastersapp.models import ItemClass
from mastersapp.models import ItemFpmasterext
from mastersapp.models import ItemUnitMaster
from mastersapp.models import ProductCategoryMaster



class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Companymaster
        fields = ['companyid', 'companyname']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employeemaster
        fields = ['empid', 'empname']

class ItemClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemClass
        fields = ['classid', 'classname']

class ItemFpmasterQualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFpmasterext
        fields = ['quality']

class UnitMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemUnitMaster
        fields = ['unitid', 'unitname']

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryMaster
        fields = ['pcategoryid', 'particular']
