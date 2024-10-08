from rest_framework import serializers
from .models import TextMatterChecking,Colorcheckingreport

class TextMatterCheckingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextMatterChecking
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.partialcheckdate:
            representation['partialcheckdate'] = instance.partialcheckdate.strftime("%Y-%m-%d %H:%M:%S")
        if instance.fullcheckdate:
            representation['fullcheckdate'] = instance.fullcheckdate.strftime("%Y-%m-%d %H:%M:%S")
        if instance.checkdate:
            representation['checkdate'] = instance.checkdate.strftime("%Y-%m-%d %H:%M:%S")
        return representation

class ColorcheckingreportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colorcheckingreport
        fields = '__all__'
        extra_kwargs = {
            'adatetime': {'required': False,'read_only': False},
            'mdatetime': {'required': False,'read_only': False},
            'delta': {'required': False, 'allow_blank': True, 'allow_null': True},
        }
        # 'mdatetime': {'read_only': True},
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.adatetime:
            representation['adatetime'] = instance.adatetime.strftime("%Y-%m-%d %H:%M:%S")
        if instance.mdatetime:
            representation['mdatetime'] = instance.mdatetime.strftime("%Y-%m-%d %H:%M:%S")
        
        return representation