# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TextMatterChecking(models.Model):
    autoid = models.AutoField(db_column='AutoId', primary_key=True)
    docid = models.CharField(db_column='DocID', unique=True, max_length=20)
    criticaldefect = models.CharField(db_column='CriticalDefect', max_length=50)
    checkdate = models.DateTimeField(db_column='CheckDate')
    partialcheckdate = models.DateTimeField(db_column='PartialCheckDate')
    fullcheckdate = models.DateTimeField(db_column='FullCheckDate')
    checkingmethod = models.CharField(db_column='CheckingMethod', max_length=50)
    checkedby = models.CharField(db_column='CheckedBy', max_length=10)
    remarks = models.CharField(db_column='Remarks', max_length=200)
    adatetime = models.DateTimeField(db_column='AdateTime', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'text_matter_checking'
