# serializers.py
from rest_framework import serializers
from .models import EstJobcomplexity
from .models import CoatingMaster
from .models import Lammaster
from .models import Windowpatchtype
from .models import Foilmaster
from .models import ItemEmbosetypeMaster
from .models import Flutemaster

class JobComplexitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EstJobcomplexity
        fields = ['id', 'name','prid','isactive']

class CoatingMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoatingMaster
        fields = ['coatingid', 'description','isactive']

class LammasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lammaster
        fields = ['lamid', 'filmtype','micron']

class WindowpatchtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Windowpatchtype
        fields = ['id', 'patch_type']

class FoilTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foilmaster
        fields = ['foilid', 'foiltype']

class ItemEmbosetypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemEmbosetypeMaster
        fields = ['typeid', 'typedescription']

class FlutemasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flutemaster
        fields = ['corrfluteid', 'flutetype']