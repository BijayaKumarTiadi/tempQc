# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Employeemaster(models.Model):
    empid = models.CharField(db_column='EmpId', primary_key=True, max_length=10)  # Field name made lowercase.
    empname = models.CharField(db_column='EmpName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    post = models.CharField(db_column='Post', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dept = models.CharField(db_column='Dept', max_length=50, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=100, blank=True, null=True)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=50, blank=True, null=True)  # Field name made lowercase.
    joindate = models.DateTimeField(db_column='JoinDate', blank=True, null=True)  # Field name made lowercase.
    isactive = models.PositiveIntegerField(db_column='IsActive')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'employeemaster'
