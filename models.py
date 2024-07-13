# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ItemWomaster(models.Model):
    awoid = models.AutoField(db_column='AWOID', primary_key=True)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  # Field name made lowercase.
    woid = models.CharField(db_column='WOID', max_length=30)  # Field name made lowercase.
    seriesid = models.CharField(db_column='SeriesID', max_length=10)  # Field name made lowercase.
    sprefix = models.CharField(db_column='SPrefix', max_length=15)  # Field name made lowercase.
    swono = models.CharField(db_column='SWONo', max_length=10)  # Field name made lowercase.
    ssufix = models.CharField(db_column='SSufix', max_length=2)  # Field name made lowercase.
    wodate = models.DateTimeField(db_column='WODate', blank=True, null=True)  # Field name made lowercase.
    postatus = models.CharField(db_column='POStatus', max_length=100)  # Field name made lowercase.
    wono = models.CharField(db_column='WONo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    podate = models.DateTimeField(db_column='PODate')  # Field name made lowercase.
    clientid = models.CharField(db_column='ClientId', max_length=10, blank=True, null=True)  # Field name made lowercase.
    execid = models.CharField(db_column='ExecId', max_length=20)  # Field name made lowercase.
    orderedby = models.CharField(db_column='OrderedBy', max_length=45, blank=True, null=True)  # Field name made lowercase.
    paymentday = models.CharField(db_column='PaymentDay', max_length=50)  # Field name made lowercase.
    paymenttype = models.CharField(db_column='PaymentType', max_length=100)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive')  # Field name made lowercase.
    auid = models.CharField(db_column='AUID', max_length=10)  # Field name made lowercase.
    adatetime = models.CharField(db_column='ADateTime', max_length=45)  # Field name made lowercase.
    muid = models.CharField(db_column='MUID', max_length=10)  # Field name made lowercase.
    mdatetime = models.CharField(db_column='MDateTime', max_length=45)  # Field name made lowercase.
    duid = models.CharField(db_column='DUID', max_length=10)  # Field name made lowercase.
    ddatetime = models.CharField(db_column='DDateTime', max_length=45)  # Field name made lowercase.
    filelocation = models.CharField(db_column='FileLocation', max_length=225)  # Field name made lowercase.
    hdpe = models.PositiveIntegerField(db_column='HDPE')  # Field name made lowercase.
    proofingchk = models.PositiveIntegerField(db_column='ProofingCHK')  # Field name made lowercase.
    unique_projectionno = models.CharField(db_column='Unique_ProjectionNo', max_length=100)  # Field name made lowercase.
    poreceivedate = models.DateTimeField(db_column='POReceiveDate')  # Field name made lowercase.
    comp_main_woid = models.CharField(db_column='Comp_Main_WOID', max_length=30)  # Field name made lowercase.
    motherfpid = models.CharField(db_column='MotherFPID', max_length=10)  # Field name made lowercase.
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  # Field name made lowercase.
    docnotion = models.IntegerField(db_column='DocNotion')  # Field name made lowercase.
    freightapplicable = models.PositiveIntegerField(db_column='FreightApplicable')  # Field name made lowercase.
    porecdate = models.CharField(db_column='PORecDate', max_length=100)  # Field name made lowercase.
    artworkdate = models.CharField(db_column='ArtWorkDate', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item_womaster'
        unique_together = (('awoid', 'woid', 'docnotion'),)
