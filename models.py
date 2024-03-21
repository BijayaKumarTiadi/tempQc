# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Papermasterfull(models.Model):
    paperid = models.CharField(db_column='PaperId', primary_key=True, max_length=10)  # Field name made lowercase.
    paperkind = models.CharField(db_column='PaperKind', max_length=50, blank=True, null=True)  # Field name made lowercase.
    manucompany = models.CharField(db_column='ManuCompany', max_length=50, blank=True, null=True)  # Field name made lowercase.
    gsm = models.IntegerField(db_column='Gsm', blank=True, null=True)  # Field name made lowercase.
    grain = models.CharField(db_column='Grain', max_length=10, blank=True, null=True)  # Field name made lowercase.
    costprice = models.FloatField(db_column='CostPrice', blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='Unit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    standardlength = models.FloatField(db_column='StandardLength', blank=True, null=True)  # Field name made lowercase.
    standardbreadth = models.FloatField(db_column='StandardBreadth', blank=True, null=True)  # Field name made lowercase.
    pquantity = models.FloatField(db_column='PQuantity', blank=True, null=True)  # Field name made lowercase.
    stock = models.CharField(db_column='Stock', max_length=20)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    shperpacket = models.SmallIntegerField(db_column='ShPerPacket', blank=True, null=True)  # Field name made lowercase.
    packetweight = models.FloatField(db_column='PacketWeight', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=50, blank=True, null=True)  # Field name made lowercase.
    isspecial = models.PositiveIntegerField(db_column='IsSpecial')  # Field name made lowercase.
    pkind = models.CharField(db_column='PKind', max_length=45)  # Field name made lowercase.
    fsctype = models.IntegerField(db_column='FSCType')  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive')  # Field name made lowercase.
    paperbrand = models.CharField(db_column='PaperBrand', max_length=30)  # Field name made lowercase.
    classid = models.CharField(db_column='Classid', max_length=10)  # Field name made lowercase.
    bf = models.IntegerField(db_column='BF')  # Field name made lowercase.
    thickness = models.FloatField(db_column='Thickness')  # Field name made lowercase.
    uom = models.CharField(db_column='UOM', max_length=10)  # Field name made lowercase.
    subgroupid = models.IntegerField(db_column='SubGroupID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'papermasterfull'
