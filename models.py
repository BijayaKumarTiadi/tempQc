# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Seriesmaster(models.Model):
    id = models.CharField(db_column='ID', max_length=10)  # Field name made lowercase.
    prefix = models.CharField(db_column='Prefix', primary_key=True, max_length=30)  # Field name made lowercase.
    docno = models.CharField(db_column='DocNo', max_length=10)  # Field name made lowercase.
    sufix = models.CharField(db_column='Sufix', max_length=10)  # Field name made lowercase.
    doctype = models.CharField(db_column='DocType', max_length=45)  # Field name made lowercase.
    isactive = models.PositiveIntegerField(db_column='IsActive')  # Field name made lowercase.
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  # Field name made lowercase.
    seriestype = models.CharField(db_column='SeriesType', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'seriesmaster'
        unique_together = (('prefix', 'icompanyid', 'doctype'),)
