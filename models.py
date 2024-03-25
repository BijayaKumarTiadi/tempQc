# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class EstProcessInputDetail(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    prid = models.CharField(db_column='PrID', max_length=50)  # Field name made lowercase.
    sp_process_no = models.IntegerField(db_column='SP_Process_no')  # Field name made lowercase.
    input_label_name = models.CharField(max_length=30)
    input_type = models.CharField(max_length=30, blank=True, null=True)
    input_data_type = models.CharField(max_length=30, blank=True, null=True)
    input_default_value = models.CharField(max_length=10, blank=True, null=True)
    seqno = models.IntegerField(db_column='SeqNo', blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'est_process_input_detail'
