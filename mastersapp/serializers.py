from rest_framework import serializers
from .models import TextMatterChecking

class TextMatterCheckingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextMatterChecking
        fields = '__all__'
