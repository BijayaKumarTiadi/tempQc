from django.db import models


class ItemWomaster(models.Model):
    woid = models.CharField(db_column='WOID', max_length=30)  
    wodate = models.DateTimeField(db_column='WODate')  
    wono = models.CharField(db_column='WONo', max_length=30)  
    clientid = models.CharField(db_column='ClientId', max_length=10)  
    remarks = models.CharField(db_column='Remarks', max_length=100)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    isactive = models.IntegerField(db_column='IsActive')  
    orderedby = models.CharField(db_column='OrderedBy', max_length=45)  
    auid = models.CharField(db_column='AUID', max_length=10)  
    adatetime = models.CharField(db_column='ADateTime', max_length=45)  
    muid = models.CharField(db_column='MUID', max_length=10)  
    mdatetime = models.CharField(db_column='MDateTime', max_length=45)  
    duid = models.CharField(db_column='DUID', max_length=10)  
    ddatetime = models.CharField(db_column='DDateTime', max_length=45)  
    filelocation = models.CharField(db_column='FileLocation', max_length=225)  
    hdpe = models.PositiveIntegerField(db_column='HDPE')  
    podate = models.DateTimeField(db_column='PODate')  
    execid = models.CharField(db_column='ExecId', max_length=20)  
    sprefix = models.CharField(db_column='SPrefix', max_length=10)  
    swono = models.CharField(db_column='SWONo', max_length=10)  
    ssufix = models.CharField(db_column='SSufix', max_length=2)  
    proofingchk = models.PositiveIntegerField(db_column='ProofingCHK')  
    paymentday = models.CharField(db_column='PaymentDay', max_length=50)  
    awoid = models.AutoField(db_column='AWOID', primary_key=True)  
    paymenttype = models.CharField(db_column='PaymentType', max_length=100)  
    postatus = models.CharField(db_column='POStatus', max_length=100)  
    unique_projectionno = models.CharField(db_column='Unique_ProjectionNo', max_length=100)  
    porecdate = models.DateTimeField(db_column='PORecDate')  
    artworkdate = models.DateTimeField(db_column='ArtWorkDate')  
    docnotion = models.IntegerField(db_column='DocNotion')  
    comp_main_woid = models.CharField(db_column='Comp_Main_WOID', max_length=30)  
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  

    class Meta:
        managed = False
        db_table = 'item_womaster'
        unique_together = (('awoid', 'woid', 'docnotion'),)
