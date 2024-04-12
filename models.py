# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class EstNewQuote(models.Model):
    quoteid = models.AutoField(db_column='QuoteID', primary_key=True)  # Field name made lowercase.
    quotedate = models.CharField(db_column='QuoteDate', max_length=10)  # Field name made lowercase.
    quote_no = models.CharField(db_column='Quote_No', max_length=30)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  # Field name made lowercase.
    clientid = models.CharField(db_column='ClientID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    client_name = models.CharField(db_column='Client_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    product_name = models.CharField(db_column='Product_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    product_code = models.CharField(db_column='Product_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    carton_type_id = models.IntegerField(db_column='Carton_Type_ID', blank=True, null=True)  # Field name made lowercase.
    auid = models.CharField(db_column='AUID', max_length=10)  # Field name made lowercase.
    adatetime = models.DateTimeField(db_column='ADateTime', blank=True, null=True)  # Field name made lowercase.
    muid = models.CharField(db_column='MUID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='MDateTime', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=200, blank=True, null=True)  # Field name made lowercase.
    orderstatus = models.CharField(db_column='OrderStatus', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    finalby = models.CharField(db_column='FinalBy', max_length=10, blank=True, null=True)  # Field name made lowercase.
    enqno = models.CharField(db_column='EnqNo', max_length=10, blank=True, null=True)  # Field name made lowercase.
    docnotion = models.IntegerField(db_column='DocNotion', blank=True, null=True)  # Field name made lowercase.
    estnotion = models.CharField(db_column='EstNotion', max_length=50, blank=True, null=True)  # Field name made lowercase.
    finaldate = models.DateTimeField(db_column='FinalDate', blank=True, null=True)  # Field name made lowercase.
    repid = models.CharField(db_column='RepID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    impexpstatus = models.CharField(db_column='ImpExpStatus', max_length=2, blank=True, null=True)  # Field name made lowercase.
    revquoteno = models.IntegerField(db_column='RevQuoteNo', blank=True, null=True)  # Field name made lowercase.
    grainstyle = models.IntegerField(db_column='GrainStyle', blank=True, null=True)  # Field name made lowercase.
    locationid = models.CharField(db_column='LocationID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    currencyid = models.CharField(db_column='CurrencyID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    currency_factctor = models.FloatField(db_column='Currency_Factctor', blank=True, null=True)  # Field name made lowercase.
    currency_curramt = models.FloatField(db_column='Currency_CurrAmt', blank=True, null=True)  # Field name made lowercase.
    clientcategoryid = models.CharField(db_column='ClientCategoryID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    calculatedrate = models.FloatField(db_column='CalculatedRate', blank=True, null=True)  # Field name made lowercase.
    quoterate = models.FloatField(db_column='QuoteRate', blank=True, null=True)  # Field name made lowercase.
    finalrate = models.FloatField(db_column='FinalRate', blank=True, null=True)  # Field name made lowercase.
    fpid = models.CharField(db_column='FPID', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Est_New_quote'
