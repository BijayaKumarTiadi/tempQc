from django.db import models

class Seriesmaster(models.Model):
    id = models.CharField(db_column='ID', max_length=10)  
    prefix = models.CharField(db_column='Prefix', primary_key=True, max_length=30)  
    docno = models.CharField(db_column='DocNo', max_length=10)  
    sufix = models.CharField(db_column='Sufix', max_length=10)  
    doctype = models.CharField(db_column='DocType', max_length=45)  
    isactive = models.PositiveIntegerField(db_column='IsActive')  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    seriestype = models.CharField(db_column='SeriesType', max_length=50)  

    class Meta:
        managed = False
        db_table = 'seriesmaster'
        unique_together = (('prefix', 'icompanyid', 'doctype'),)


class Companymaster(models.Model):
    companyid = models.CharField(db_column='CompanyId', primary_key=True, max_length=10)  
    companyname = models.CharField(db_column='CompanyName', max_length=100, blank=True, null=True)  
    shortname = models.CharField(db_column='ShortName', max_length=4, blank=True, null=True)  
    exciseper = models.FloatField(db_column='ExcisePer', blank=True, null=True)  
    localtaxper = models.FloatField(db_column='LocalTaxPer', blank=True, null=True)  
    carryingandforper = models.FloatField(db_column='CarryingAndForPer', blank=True, null=True)  
    packagingper = models.FloatField(db_column='PackagingPer', blank=True, null=True)  
    catid = models.CharField(db_column='CatID', max_length=10, blank=True, null=True)  
    isactive = models.PositiveIntegerField(db_column='IsActive')  
    creditterm = models.CharField(db_column='CreditTerm', max_length=50, blank=True, null=True)  
    cfminrate = models.FloatField(db_column='CFMinRate', blank=True, null=True)  
    cfminqty = models.FloatField(db_column='CFMinQty', blank=True, null=True)  
    cfkg = models.FloatField(db_column='CFKG', blank=True, null=True)  
    creditlimit = models.FloatField(db_column='CreditLimit', blank=True, null=True)  
    repid = models.CharField(db_column='RepID', max_length=10, blank=True, null=True)  
    weburl = models.CharField(db_column='WebURL', max_length=50, blank=True, null=True)  
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  
    isosvendor = models.PositiveIntegerField(db_column='IsOSVendor')  
    mantaininventory = models.PositiveIntegerField(db_column='MantainInventory')  
    packtemplate = models.CharField(db_column='PackTemplate', max_length=10)  
    commtemplate = models.CharField(db_column='CommTemplate', max_length=10)  
    eccno = models.CharField(db_column='ECCNo', max_length=45)  
    tin = models.CharField(db_column='TIN', max_length=45)  
    cstno = models.CharField(db_column='CSTNo', max_length=45)  
    payid = models.CharField(db_column='PayID', max_length=10, blank=True, null=True)  
    auid = models.CharField(db_column='AUID', max_length=10, blank=True, null=True)  
    adatetime = models.DateTimeField(db_column='ADateTime', blank=True, null=True)  
    muid = models.CharField(db_column='MUID', max_length=10)  
    mdatetime = models.CharField(db_column='MDateTime', max_length=50)  
    lstno = models.CharField(db_column='LSTNo', max_length=45)  
    shortname2 = models.CharField(db_column='ShortName2', max_length=60)  
    exciselicno = models.CharField(db_column='ExciseLicNo', max_length=45)  
    collectrate = models.CharField(db_column='Collectrate', max_length=45)  
    rangename = models.CharField(db_column='RangeName', max_length=45)  
    division = models.CharField(db_column='Division', max_length=45)  
    rangeadd = models.CharField(db_column='RangeAdd', max_length=250)  
    tanno = models.CharField(db_column='TANNo', max_length=45)  
    divadd = models.CharField(db_column='DivAdd', max_length=45)  
    clientstatus = models.CharField(db_column='ClientStatus', max_length=1)  
    clientgroup = models.CharField(db_column='ClientGroup', max_length=1)  
    ismother = models.IntegerField(db_column='Ismother')  
    motherid = models.CharField(db_column='Motherid', max_length=10)  
    lbtno = models.CharField(db_column='LBTNo', max_length=50)  
    segment = models.CharField(max_length=50, blank=True, null=True)
    delaytime = models.IntegerField(db_column='DelayTime')  
    cinno = models.CharField(db_column='CINNo', max_length=50)  
    plusmiusorderaccptance = models.FloatField(db_column='Plusmiusorderaccptance')  
    onhold = models.IntegerField(db_column='OnHold')  
    holdreason = models.CharField(db_column='HoldReason', max_length=100)  
    gstin = models.CharField(db_column='GSTIN', max_length=15)  
    labourprofitper = models.FloatField(db_column='LabourProfitPer')  
    type_dom_exp = models.CharField(db_column='Type_Dom_Exp', max_length=50)  
    transportationper = models.FloatField(db_column='Transportationper')  
    clientkey = models.CharField(db_column='Clientkey', max_length=8)  
    freightbyus = models.IntegerField(db_column='Freightbyus')  
    iswastage = models.IntegerField(db_column='IsWastage')  
    poselection = models.IntegerField(db_column='POSelection')  

    class Meta:
        managed = False
        db_table = 'companymaster'
        unique_together = (('companyid', 'ismother'),)



class Employeemaster(models.Model):
    empid = models.CharField(db_column='EmpId', primary_key=True, max_length=10)  
    empname = models.CharField(db_column='EmpName', max_length=50, blank=True, null=True)  
    post = models.CharField(db_column='Post', max_length=50, blank=True, null=True)  
    dept = models.CharField(db_column='Dept', max_length=50, blank=True, null=True)  
    address = models.CharField(db_column='Address', max_length=100, blank=True, null=True)  
    phone = models.CharField(db_column='Phone', max_length=50, blank=True, null=True)  
    joindate = models.DateTimeField(db_column='JoinDate', blank=True, null=True)  
    isactive = models.PositiveIntegerField(db_column='IsActive')  

    class Meta:
        managed = False
        db_table = 'employeemaster'