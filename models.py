# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ItemSpec(models.Model):
    specid = models.CharField(db_column='SpecID', primary_key=True, max_length=10)  # Field name made lowercase.
    itemid = models.CharField(db_column='ItemID', max_length=10)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='ICompanyID', max_length=20)  # Field name made lowercase.
    info1 = models.CharField(db_column='Info1', max_length=100)  # Field name made lowercase.
    info2 = models.CharField(db_column='Info2', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item_spec'
        unique_together = (('specid', 'itemid', 'description'),)
