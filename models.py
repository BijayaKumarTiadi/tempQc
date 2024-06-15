# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Companymaster(models.Model):
    companyid = models.CharField(db_column='CompanyId', primary_key=True, max_length=10)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    shortname = models.CharField(db_column='ShortName', max_length=4, blank=True, null=True)  # Field name made lowercase.
    exciseper = models.FloatField(db_column='ExcisePer', blank=True, null=True)  # Field name made lowercase.
    localtaxper = models.FloatField(db_column='LocalTaxPer', blank=True, null=True)  # Field name made lowercase.
    carryingandforper = models.FloatField(db_column='CarryingAndForPer', blank=True, null=True)  # Field name made lowercase.
    packagingper = models.FloatField(db_column='PackagingPer', blank=True, null=True)  # Field name made lowercase.
    catid = models.CharField(db_column='CatID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    isactive = models.PositiveIntegerField(db_column='IsActive')  # Field name made lowercase.
    creditterm = models.CharField(db_column='CreditTerm', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cfminrate = models.FloatField(db_column='CFMinRate', blank=True, null=True)  # Field name made lowercase.
    cfminqty = models.FloatField(db_column='CFMinQty', blank=True, null=True)  # Field name made lowercase.
    cfkg = models.FloatField(db_column='CFKG', blank=True, null=True)  # Field name made lowercase.
    creditlimit = models.FloatField(db_column='CreditLimit', blank=True, null=True)  # Field name made lowercase.
    repid = models.CharField(db_column='RepID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    weburl = models.CharField(db_column='WebURL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.
    isosvendor = models.PositiveIntegerField(db_column='IsOSVendor')  # Field name made lowercase.
    mantaininventory = models.PositiveIntegerField(db_column='MantainInventory')  # Field name made lowercase.
    packtemplate = models.CharField(db_column='PackTemplate', max_length=10)  # Field name made lowercase.
    commtemplate = models.CharField(db_column='CommTemplate', max_length=10)  # Field name made lowercase.
    eccno = models.CharField(db_column='ECCNo', max_length=45)  # Field name made lowercase.
    tin = models.CharField(db_column='TIN', max_length=45)  # Field name made lowercase.
    cstno = models.CharField(db_column='CSTNo', max_length=45)  # Field name made lowercase.
    payid = models.CharField(db_column='PayID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    auid = models.CharField(db_column='AUID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    adatetime = models.DateTimeField(db_column='ADateTime', blank=True, null=True)  # Field name made lowercase.
    muid = models.CharField(db_column='MUID', max_length=10)  # Field name made lowercase.
    mdatetime = models.CharField(db_column='MDateTime', max_length=50)  # Field name made lowercase.
    lstno = models.CharField(db_column='LSTNo', max_length=45)  # Field name made lowercase.
    shortname2 = models.CharField(db_column='ShortName2', max_length=60)  # Field name made lowercase.
    exciselicno = models.CharField(db_column='ExciseLicNo', max_length=45)  # Field name made lowercase.
    collectrate = models.CharField(db_column='Collectrate', max_length=45)  # Field name made lowercase.
    rangename = models.CharField(db_column='RangeName', max_length=45)  # Field name made lowercase.
    division = models.CharField(db_column='Division', max_length=45)  # Field name made lowercase.
    rangeadd = models.CharField(db_column='RangeAdd', max_length=250)  # Field name made lowercase.
    tanno = models.CharField(db_column='TANNo', max_length=45)  # Field name made lowercase.
    divadd = models.CharField(db_column='DivAdd', max_length=45)  # Field name made lowercase.
    clientstatus = models.CharField(db_column='ClientStatus', max_length=1)  # Field name made lowercase.
    clientgroup = models.CharField(db_column='ClientGroup', max_length=1)  # Field name made lowercase.
    ismother = models.IntegerField(db_column='Ismother')  # Field name made lowercase.
    motherid = models.CharField(db_column='Motherid', max_length=10)  # Field name made lowercase.
    lbtno = models.CharField(db_column='LBTNo', max_length=50)  # Field name made lowercase.
    segment = models.CharField(max_length=50, blank=True, null=True)
    delaytime = models.IntegerField(db_column='DelayTime')  # Field name made lowercase.
    cinno = models.CharField(db_column='CINNo', max_length=50)  # Field name made lowercase.
    plusmiusorderaccptance = models.FloatField(db_column='Plusmiusorderaccptance')  # Field name made lowercase.
    onhold = models.IntegerField(db_column='OnHold')  # Field name made lowercase.
    holdreason = models.CharField(db_column='HoldReason', max_length=100)  # Field name made lowercase.
    gstin = models.CharField(db_column='GSTIN', max_length=15)  # Field name made lowercase.
    labourprofitper = models.FloatField(db_column='LabourProfitPer')  # Field name made lowercase.
    type_dom_exp = models.CharField(db_column='Type_Dom_Exp', max_length=50)  # Field name made lowercase.
    transportationper = models.FloatField(db_column='Transportationper')  # Field name made lowercase.
    clientkey = models.CharField(db_column='Clientkey', max_length=8)  # Field name made lowercase.
    freightbyus = models.IntegerField(db_column='Freightbyus')  # Field name made lowercase.
    iswastage = models.IntegerField(db_column='IsWastage')  # Field name made lowercase.
    poselection = models.IntegerField(db_column='POSelection')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'companymaster'
        unique_together = (('companyid', 'ismother'),)
