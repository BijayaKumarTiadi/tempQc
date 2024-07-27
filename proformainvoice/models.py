from django.db import models

# models for workworder

class ItemPiDetail(models.Model):
    internalid = models.AutoField(db_column='InternalID', primary_key=True)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    docid = models.CharField(db_column='Docid', max_length=30)  
    rowno = models.IntegerField(db_column='Rowno')  
    itemid = models.CharField(db_column='ItemID', max_length=10)  
    itemcode = models.CharField(db_column='ItemCode', max_length=40)  
    codeno = models.CharField(db_column='CodeNo', max_length=45)  
    itemdesc = models.CharField(db_column='ItemDesc', max_length=1000)  
    quantity = models.IntegerField(db_column='Quantity')  
    percentvar = models.FloatField(db_column='PercentVar')  
    qtyplus = models.FloatField(db_column='QtyPlus')  
    qtyminus = models.FloatField(db_column='QtyMinus')  
    unitid = models.CharField(db_column='UnitID', max_length=10)  
    rate = models.FloatField(db_column='Rate')  
    rateunit = models.CharField(db_column='Rateunit', max_length=10)  
    amount = models.FloatField(db_column='Amount')  
    freight = models.FloatField(db_column='Freight')  
    insurance = models.FloatField(db_column='Insurance')  
    specification = models.CharField(db_column='Specification', max_length=10)  
    remarks = models.CharField(db_column='Remarks', max_length=1000)  
    isactive = models.IntegerField(db_column='IsActive')  
    hold = models.IntegerField(db_column='Hold')  
    clstatus = models.IntegerField(db_column='CLStatus')  
    approved = models.FloatField(db_column='Approved')  
    approvedby = models.CharField(db_column='ApprovedBy', max_length=45)  
    approvaldate = models.DateTimeField(db_column='ApprovalDate')  
    invoiceqty = models.FloatField(db_column='InvoiceQty', blank=True, null=True)  
    constatus = models.CharField(db_column='ConStatus', max_length=200, blank=True, null=True)  
    lastupdatedon = models.DateTimeField(db_column='LastUpdatedOn', blank=True, null=True)  
    templateid = models.CharField(db_column='TemplateID', max_length=20)  
    rateinthousand = models.FloatField(db_column='RateInThousand')  
    extra1 = models.CharField(db_column='Extra1', max_length=100)  
    extra2 = models.CharField(db_column='Extra2', max_length=100)  
    extra3 = models.CharField(db_column='Extra3', max_length=100)  
    extra4 = models.CharField(db_column='Extra4', max_length=100)  
    extra5 = models.CharField(db_column='Extra5', max_length=100)  
    closedate = models.DateTimeField(db_column='CloseDate')  
    closeby = models.CharField(db_column='CloseBy', max_length=10, blank=True, null=True)  
    closereason = models.CharField(db_column='CloseReason', max_length=250)  
    docnotion = models.IntegerField(db_column='DocNotion')  
    orderqty = models.IntegerField(db_column='Orderqty')  

    class Meta:
        managed = False
        db_table = 'item_pi_detail'
        unique_together = (('internalid', 'docnotion'),)



class Paymentterms(models.Model):
    payid = models.CharField(db_column='PayID', primary_key=True, max_length=10) 
    narration = models.CharField(db_column='Narration', max_length=200) 
    interestper = models.FloatField(db_column='InterestPer') 
    isactive = models.PositiveIntegerField(db_column='IsActive') 

    class Meta:
        managed = False
        db_table = 'paymentterms'


class ItemSpec(models.Model):
    specid = models.CharField(db_column='SpecID', primary_key=True, max_length=10)  
    itemid = models.CharField(db_column='ItemID', max_length=10)  
    description = models.CharField(db_column='Description', max_length=100)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=20)  
    info1 = models.CharField(db_column='Info1', max_length=100)  
    info2 = models.CharField(db_column='Info2', max_length=100)  

    class Meta:
        managed = False
        db_table = 'item_spec'
        unique_together = (('specid', 'itemid', 'description'),)

class Mypref(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    heading = models.CharField(db_column='Heading', max_length=100)  
    mainheading = models.CharField(db_column='MainHeading', max_length=100)  
    result = models.CharField(db_column='Result', max_length=100)  
    defultresult = models.CharField(db_column='DefultResult', max_length=100)  

    class Meta:
        managed = False
        db_table = 'mypref'


class ItemWomaster(models.Model):
    awoid = models.AutoField(db_column='AWOID', primary_key=True)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    seriesid = models.CharField(db_column='SeriesID', max_length=10)
    woid = models.CharField(db_column='WOID', max_length=30)  
    sprefix = models.CharField(db_column='SPrefix', max_length=15)  
    swono = models.CharField(db_column='SWONo', max_length=10)  
    ssufix = models.CharField(db_column='SSufix', max_length=2, blank=True)  
    wodate = models.DateTimeField(db_column='WODate', blank=True, null=True)  
    postatus = models.CharField(db_column='POStatus', max_length=100)  
    wono = models.CharField(db_column='WONo', max_length=30, blank=True, null=True)  
    podate = models.DateTimeField(db_column='PODate')  
    clientid = models.CharField(db_column='ClientId', max_length=10, blank=True, null=True)  
    execid = models.CharField(db_column='ExecId', max_length=20)  
    orderedby = models.CharField(db_column='OrderedBy', max_length=45, blank=True, null=True)  
    paymentday = models.CharField(db_column='PaymentDay', max_length=50)  
    paymenttype = models.CharField(db_column='PaymentType', max_length=100)  
    remarks = models.CharField(db_column='Remarks', max_length=100, blank=True, null=True)  
    isactive = models.IntegerField(db_column='IsActive' , default=0)  
    auid = models.CharField(db_column='AUID', max_length=10)  
    adatetime = models.CharField(db_column='ADateTime', max_length=45)  
    muid = models.CharField(db_column='MUID', max_length=10)  
    mdatetime = models.CharField(db_column='MDateTime', max_length=45)  
    duid = models.CharField(db_column='DUID', max_length=10)  
    ddatetime = models.CharField(db_column='DDateTime', max_length=45)  
    filelocation = models.CharField(db_column='FileLocation', max_length=225)  
    hdpe = models.PositiveIntegerField(db_column='HDPE', default=0)  
    proofingchk = models.PositiveIntegerField(db_column='ProofingCHK')  
    unique_projectionno = models.CharField(db_column='Unique_ProjectionNo', max_length=100)  
    poreceivedate = models.DateTimeField(db_column='POReceiveDate')  
    comp_main_woid = models.CharField(db_column='Comp_Main_WOID', max_length=30)  
    motherfpid = models.CharField(db_column='MotherFPID', max_length=10)  
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  
    docnotion = models.IntegerField(db_column='DocNotion')  
    freightapplicable = models.PositiveIntegerField(db_column='FreightApplicable' , default=0)  
    porecdate = models.CharField(db_column='PORecDate', max_length=100)  
    artworkdate = models.CharField(db_column='ArtWorkDate', max_length=100)  

    class Meta:
        managed = False
        db_table = 'item_pi_master'
        unique_together = (('awoid', 'woid', 'docnotion'),)