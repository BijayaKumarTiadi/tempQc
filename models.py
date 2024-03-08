# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Usermaster(models.Model):
    userid = models.CharField(db_column='UserID', primary_key=True, max_length=10)  # Field name made lowercase.
    userdepartmentid = models.CharField(db_column='UserDepartmentID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    employeecode = models.CharField(db_column='EmployeeCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    userloginname = models.CharField(db_column='UserLoginName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    userpassword = models.CharField(db_column='UserPassword', max_length=50, blank=True, null=True)  # Field name made lowercase.
    post = models.CharField(db_column='Post', max_length=100, blank=True, null=True)  # Field name made lowercase.
    joining_date = models.CharField(db_column='Joining_Date', max_length=20, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=500, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=100, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=100, blank=True, null=True)  # Field name made lowercase.
    dateofbirth = models.CharField(db_column='DateofBirth', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ph1 = models.CharField(db_column='Ph1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ph2 = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(db_column='Fax', max_length=20, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=100)  # Field name made lowercase.
    referreddby = models.CharField(db_column='ReferreddBy', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    auid = models.CharField(db_column='AUID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    adatetime = models.DateTimeField(db_column='ADateTime')  # Field name made lowercase.
    muid = models.CharField(db_column='MUID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.CharField(db_column='MDateTime', max_length=50)  # Field name made lowercase.
    companyid = models.IntegerField(db_column='CompanyID', blank=True, null=True)  # Field name made lowercase.
    mgtlevels = models.IntegerField(db_column='MgtLevels', blank=True, null=True)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='Icompanyid', max_length=10)  # Field name made lowercase.
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usermaster'
        unique_together = (('userid', 'email'),)
