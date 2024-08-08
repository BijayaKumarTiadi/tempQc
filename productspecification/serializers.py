# serializers.py
from rest_framework import serializers
from .models import EstJobcomplexity
from .models import CoatingMaster
from .models import Lammaster
from .models import Windowpatchtype
from .models import Foilmaster
from .models import ItemEmbosetypeMaster
from .models import Flutemaster
from .models import ItemMachinenames
from .models import ItemProcessname
from mastersapp.models import ItemGroupMaster
from .models import GeneralDropdown
from .models import Lammetpetmaster
from .models import Pastingmaster
from .models import Extracostmaster

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

class MachineProcessSerializer(serializers.Serializer):
    MachineID = serializers.IntegerField()
    RecID = serializers.IntegerField()
    MachineName = serializers.CharField(max_length=255)
    PrID = serializers.CharField()
    PrName = serializers.CharField(max_length=255)
    Description = serializers.CharField(max_length=255)

class ItemGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemGroupMaster
        fields = ['groupid', 'groupname']

class GeneralDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralDropdown
        fields = ['option','value']
        # fields = '__all__'

class LammetpetmasterSerializer(serializers.ModelSerializer):
    film_micron = serializers.SerializerMethodField()

    class Meta:
        model = Lammetpetmaster
        fields = ['lamid', 'film_micron']

    def get_film_micron(self, obj):
        return f"{obj.filmtype} - {obj.micron}"
    
class PastingmasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pastingmaster
        fields = ['pastingid', 'narration']

class ExtracostmasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extracostmaster
        fields = ['cprocessno', 'pname']