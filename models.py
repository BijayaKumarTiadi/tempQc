# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class EstItemtypemaster(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    cartontype = models.CharField(db_column='CartonType', max_length=60)  # Field name made lowercase.
    internalcartontype = models.CharField(db_column='internalCartonType', unique=True, max_length=60)  # Field name made lowercase.
    imgpath = models.CharField(db_column='ImgPath', max_length=200, blank=True, null=True)  # Field name made lowercase.
    ecma_code = models.CharField(db_column='ECMA_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_itemtypemaster'
        unique_together = (('id', 'cartontype'),)
