# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Currencymaster(models.Model):
    currencyid = models.CharField(db_column='CurrencyID', primary_key=True, max_length=10)  # Field name made lowercase.
    currencyname = models.CharField(db_column='CurrencyName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    currencysymbol = models.CharField(db_column='CurrencySymbol', max_length=20, db_collation='utf8_general_ci', blank=True, null=True)  # Field name made lowercase.
    isdefault = models.PositiveIntegerField(db_column='IsDefault')  # Field name made lowercase.
    hexacode = models.CharField(db_column='HexaCode', max_length=6)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'currencymaster'
