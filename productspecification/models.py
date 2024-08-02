from django.db import models

class EstJobcomplexity(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10)
    name = models.CharField(db_column='Name', max_length=40)
    remark = models.CharField(db_column='Remark', max_length=100, blank=True, null=True)
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)
    prid = models.CharField(db_column='PrID', max_length=50)
    isdefault = models.PositiveIntegerField(db_column='IsDefault')
    prwastage_per = models.FloatField(db_column='PrWastage_per')

    class Meta:
        managed = False
        db_table = 'est_jobcomplexity'
        unique_together = (('id', 'name', 'prid'), ('name', 'prid'),)

class CoatingMaster(models.Model):
    coatingid = models.CharField(db_column='CoatingID', primary_key=True, max_length=10)
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)
    isactive = models.PositiveIntegerField(db_column='IsActive', blank=True, null=True)
    cgsm = models.FloatField(db_column='CGSM')
    fullcoatingunit = models.CharField(db_column='FullCoatingUnit', max_length=45)
    fullrate = models.FloatField(db_column='FullRate')
    fullratemin = models.FloatField(db_column='FullRateMin')
    fullmincharges = models.FloatField(db_column='FullMinCharges')
    spotcoatingunit = models.CharField(db_column='SpotCoatingUnit', max_length=45)
    spotrate = models.FloatField(db_column='SpotRate')
    spotratemin = models.FloatField(db_column='SpotRateMin')
    spotratetsh = models.FloatField(db_column='SpotRateTSh')
    spotratetshmin = models.FloatField(db_column='SpotRateTShMin')
    spotmincharges = models.FloatField(db_column='SpotMinCharges')
    minratepersh = models.FloatField(db_column='MinRatePerSh')
    roundoffshby = models.FloatField(db_column='RoundOffShBy')
    mreadywastsh = models.FloatField(db_column='MReadyWastSh')
    runwastper = models.FloatField(db_column='RunWastPer')
    catid = models.CharField(db_column='CatID', max_length=10)
    machineid = models.CharField(db_column='MachineId', max_length=10)
    is_uv_coating = models.IntegerField(db_column='Is_uv_coating', blank=True, null=True)
    extra_plates = models.IntegerField(db_column='Extra_Plates', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Coating_Master'
        unique_together = (('description', 'catid'),)

class Lammaster(models.Model):
    lamid = models.CharField(db_column='LamID', primary_key=True, max_length=10)
    filmtype = models.CharField(db_column='FilmType', max_length=50, blank=True, null=True)
    micron = models.SmallIntegerField(db_column='Micron', blank=True, null=True)
    gravity = models.FloatField(db_column='Gravity', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lammaster'

class Windowpatchtype(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10)
    patch_type = models.CharField(db_column='Patch_Type', max_length=50)
    isactive = models.PositiveIntegerField(db_column='IsActive')
    isdefault = models.IntegerField(db_column='IsDefault', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'windowpatchtype'

class Foilmaster(models.Model):
    foilid = models.CharField(db_column='FoilID', primary_key=True, max_length=10)
    foiltype = models.CharField(db_column='FoilType', max_length=50, blank=True, null=True)
    minarea = models.SmallIntegerField(db_column='MinArea', blank=True, null=True)
    rolllength = models.FloatField(db_column='RollLength')
    rollwidth = models.FloatField(db_column='RollWidth')

    class Meta:
        managed = False
        db_table = 'foilmaster'

class ItemEmbosetypeMaster(models.Model):
    typeid = models.AutoField(db_column='TypeID', primary_key=True)
    typedescription = models.CharField(db_column='TypeDescription', max_length=100)
    purpose = models.CharField(db_column='Purpose', max_length=1)
    ratepersqcm = models.FloatField(db_column='RatePerSqCm')
    minarea = models.FloatField(db_column='MinArea')
    minamount = models.FloatField(db_column='MinAmount')
    blocklife = models.FloatField(db_column='BlockLife')
    isactive = models.PositiveIntegerField(db_column='IsActive')

    class Meta:
        managed = False
        db_table = 'item_embosetype_master'

class Flutemaster(models.Model):
    corrfluteid = models.CharField(db_column='CorrFluteId', primary_key=True, max_length=10)
    flutetype = models.CharField(db_column='FluteType', max_length=50, blank=True, null=True)
    extraconsumption = models.IntegerField(db_column='ExtraConsumption', blank=True, null=True)
    declinebf = models.IntegerField(db_column='DeclineBF', blank=True, null=True)
    avgthickness = models.FloatField(db_column='AvgThickness', blank=True, null=True)
    isactive = models.PositiveIntegerField(db_column='IsActive')
    flutefactor = models.FloatField(db_column='FluteFactor')
    minsheetarea = models.FloatField(db_column='MinSheetArea')
    bbadherate = models.FloatField(db_column='BBAdheRate')
    bbpastinglabour = models.FloatField(db_column='BBPastingLabour')
    ply3_1 = models.FloatField(db_column='Ply3_1')
    ply3_2 = models.FloatField(db_column='Ply3_2')
    ply3_3 = models.FloatField(db_column='Ply3_3')
    ply5_1 = models.FloatField(db_column='Ply5_1')
    ply5_2 = models.FloatField(db_column='Ply5_2')
    ply5_3 = models.FloatField(db_column='Ply5_3')
    ply7_1 = models.FloatField(db_column='Ply7_1')
    ply7_2 = models.FloatField(db_column='Ply7_2')
    ply7_3 = models.FloatField(db_column='Ply7_3')
    plyb_1 = models.FloatField(db_column='PlyB_1')
    plyb_2 = models.FloatField(db_column='PlyB_2')
    plyb_3 = models.FloatField(db_column='PlyB_3')
    makerdysheet = models.FloatField(db_column='MakeRdySheet')
    wastagerunning = models.FloatField(db_column='WastageRunning')

    class Meta:
        managed = False
        db_table = 'flutemaster'

class ItemMachinenames(models.Model):
    machineid = models.CharField(db_column='MachineID', max_length=10)
    machinename = models.CharField(db_column='MachineName', max_length=45)
    prid = models.CharField(db_column='PrID', max_length=10)
    processname = models.CharField(db_column='ProcessName', max_length=200)
    basepruniqueid = models.IntegerField(db_column='BasePrUniqueID')
    perhrruncost = models.FloatField(db_column='PerHrRunCost')
    powercharges = models.FloatField(db_column='Powercharges')
    labourcharges = models.FloatField()
    interestamt = models.FloatField(db_column='interestAmt')
    depriamt = models.FloatField()
    avgspeed = models.FloatField()
    avgsetuptime = models.FloatField()
    avgwastage = models.FloatField()
    rentpm = models.FloatField()
    maintainpm = models.FloatField()
    consumblepm = models.FloatField()
    capacityperday = models.FloatField(db_column='CapacityPerDay', blank=True, null=True)
    inuse = models.IntegerField(db_column='InUse', blank=True, null=True)
    recid = models.AutoField(db_column='Recid', primary_key=True)
    machineno_internal = models.CharField(db_column='MachineNo_Internal', max_length=20, blank=True, null=True)
    makereadycostnr = models.IntegerField(db_column='MakeReadyCostNr', blank=True, null=True)
    productioncostnr = models.IntegerField(db_column='ProductionCostNr', blank=True, null=True)
    makereadycostuv = models.IntegerField(db_column='MakeReadyCostUV', blank=True, null=True)
    productioncostuv = models.IntegerField(db_column='ProductionCostUV', blank=True, null=True)
    directmanpowcost = models.IntegerField(db_column='DirectManpowCost', blank=True, null=True)
    supportmanpowcost = models.IntegerField(db_column='SupportManpowCost', blank=True, null=True)
    admindepmanpowcost = models.IntegerField(db_column='AdminDepManpowCost', blank=True, null=True)
    pile_height = models.SmallIntegerField()
    pile_weight_limit = models.SmallIntegerField()
    pile_load_time = models.IntegerField()
    speedunit = models.CharField(db_column='SpeedUnit', max_length=10, blank=True, null=True)
    icompanyid = models.CharField(max_length=10)
    arrangeseqno = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'item_machinenames'

class ItemProcessname(models.Model):
    prid = models.CharField(db_column='PrID', unique=True, max_length=50)
    prname = models.CharField(db_column='PrName', max_length=45)
    description = models.CharField(db_column='Description', max_length=45)
    unitid = models.CharField(db_column='UnitID', max_length=20)
    isactive = models.PositiveIntegerField(db_column='IsActive')
    level = models.FloatField(db_column='Level')
    narration = models.CharField(max_length=200)
    inputuom = models.CharField(db_column='InputUOM', max_length=10)
    outputuom = models.CharField(db_column='OutPutUOM', max_length=10)
    prodvalidation = models.PositiveIntegerField(db_column='ProdValidation')
    displayinlistbox = models.FloatField(db_column='DisplayInListBox')
    basepruniqueid = models.IntegerField(db_column='BasePrUniqueID')
    basetablename = models.CharField(db_column='BaseTableName', max_length=200)
    canbeonline = models.FloatField(db_column='CanBeOnLine')
    formno = models.CharField(db_column='FormNo', max_length=100)
    donebycontractor = models.IntegerField(db_column='DonebyContractor')
    mrwastage = models.FloatField(db_column='MrWastage')
    processwastage = models.FloatField(db_column='ProcessWastage')
    wastagein = models.CharField(db_column='WastageIn', max_length=10)
    id = models.AutoField(db_column='ID', primary_key=True)
    tseqno = models.IntegerField(db_column='Tseqno')

    class Meta:
        managed = False
        db_table = 'item_processname'
        unique_together = (('id', 'prid'),)