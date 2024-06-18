from django.db import models


class ItemWomaster(models.Model):
    woid = models.CharField(db_column='WOID', max_length=30)  
    wodate = models.DateTimeField(db_column='WODate')  
    wono = models.CharField(db_column='WONo', max_length=30)  
    clientid = models.CharField(db_column='ClientId', max_length=10)  
    remarks = models.CharField(db_column='Remarks', max_length=100)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    isactive = models.IntegerField(db_column='IsActive')  
    orderedby = models.CharField(db_column='OrderedBy', max_length=45)  
    auid = models.CharField(db_column='AUID', max_length=10)  
    adatetime = models.CharField(db_column='ADateTime', max_length=45)  
    muid = models.CharField(db_column='MUID', max_length=10)  
    mdatetime = models.CharField(db_column='MDateTime', max_length=45)  
    duid = models.CharField(db_column='DUID', max_length=10)  
    ddatetime = models.CharField(db_column='DDateTime', max_length=45)  
    filelocation = models.CharField(db_column='FileLocation', max_length=225)  
    hdpe = models.PositiveIntegerField(db_column='HDPE')  
    podate = models.DateTimeField(db_column='PODate')  
    execid = models.CharField(db_column='ExecId', max_length=20)  
    sprefix = models.CharField(db_column='SPrefix', max_length=10)  
    swono = models.CharField(db_column='SWONo', max_length=10)  
    ssufix = models.CharField(db_column='SSufix', max_length=2)  
    proofingchk = models.PositiveIntegerField(db_column='ProofingCHK')  
    paymentday = models.CharField(db_column='PaymentDay', max_length=50)  
    awoid = models.AutoField(db_column='AWOID', primary_key=True)  
    paymenttype = models.CharField(db_column='PaymentType', max_length=100)  
    postatus = models.CharField(db_column='POStatus', max_length=100)  
    unique_projectionno = models.CharField(db_column='Unique_ProjectionNo', max_length=100)  
    porecdate = models.DateTimeField(db_column='PORecDate')  
    artworkdate = models.DateTimeField(db_column='ArtWorkDate')  
    docnotion = models.IntegerField(db_column='DocNotion')  
    comp_main_woid = models.CharField(db_column='Comp_Main_WOID', max_length=30)  
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  

    class Meta:
        managed = False
        db_table = 'item_womaster'
        unique_together = (('awoid', 'woid', 'docnotion'),)


# models for workworder

class ItemWodetail(models.Model):
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    woid = models.CharField(db_column='WOId', max_length=30)  
    jobno = models.CharField(db_column='JobNo', primary_key=True, max_length=20)  
    rowno = models.IntegerField(db_column='Rowno')  
    estimateno = models.CharField(db_column='EstimateNo', max_length=30)  
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
    amount = models.FloatField(db_column='Amount')  
    packing = models.FloatField(db_column='Packing')  
    freight = models.FloatField(db_column='Freight')  
    insurance = models.FloatField(db_column='Insurance')  
    specification = models.CharField(db_column='Specification', max_length=10)  
    ref = models.CharField(max_length=45)
    color = models.CharField(max_length=45)
    cp = models.CharField(db_column='CP', max_length=1, blank=True, null=True)  
    remarks = models.TextField(db_column='Remarks')  
    remarkinv = models.TextField(db_column='RemarkInv')  
    qtydispatched = models.FloatField(db_column='QtyDispatched')  
    modeoftrans = models.CharField(db_column='ModeOfTrans', max_length=50)  
    fgtype = models.CharField(max_length=30)
    isactive = models.IntegerField(db_column='IsActive')  
    transfer_wo = models.IntegerField()
    chrgetype1 = models.CharField(max_length=45)
    chargevalue1 = models.CharField(max_length=45)
    chrgetype2 = models.CharField(max_length=45)
    chargevalue2 = models.CharField(max_length=45)
    chrgetype3 = models.CharField(max_length=45)
    chargevalue3 = models.CharField(max_length=45)
    totjobcardqty = models.IntegerField(db_column='Totjobcardqty')  
    dontshowforjc = models.IntegerField(db_column='DontShowForJc', blank=True, null=True)  
    hold = models.IntegerField(db_column='Hold')  
    clstatus = models.PositiveIntegerField(db_column='CLStatus')  
    approved = models.FloatField(db_column='Approved')  
    approvedby = models.CharField(db_column='ApprovedBy', max_length=45)  
    approvaldate = models.DateTimeField(db_column='ApprovalDate')  
    appremarks = models.CharField(db_column='AppRemarks', max_length=45)  
    deldate = models.CharField(db_column='DelDate', max_length=30)  
    recordid = models.CharField(db_column='RecordID', max_length=30)  
    diladd = models.TextField(db_column='DilAdd')  
    delschedule = models.TextField(db_column='DelSchedule')  
    artworkno = models.CharField(db_column='ArtWorkNo', max_length=45)  
    addressid = models.CharField(db_column='AddressID', max_length=250)  
    addqty = models.CharField(db_column='AddQty', max_length=250)  
    shadecardid = models.CharField(db_column='ShadeCardID', max_length=45)  
    commitdt = models.CharField(db_column='CommitDt', max_length=20)  
    commitschedule = models.TextField(db_column='CommitSchedule')  
    exciseduty = models.FloatField(db_column='ExciseDuty')  
    edcess = models.FloatField(db_column='EDCESS')  
    shecess = models.FloatField(db_column='SHECESS')  
    vat = models.FloatField(db_column='VAT')  
    cst = models.FloatField(db_column='CST')  
    servicetax = models.FloatField(db_column='ServiceTax')  
    extracol = models.FloatField(db_column='ExtraCol')  
    salestype = models.CharField(db_column='SalesType', max_length=50)  
    internaljobno = models.CharField(db_column='InternalJobNo', max_length=50)  
    internaljobdate = models.CharField(db_column='InternalJobDate', max_length=50)  
    internalestimateno = models.CharField(db_column='InternalEstimateNo', max_length=50)  
    internalestimatedate = models.CharField(db_column='InternalEstimateDate', max_length=50)  
    proofingstatus = models.CharField(db_column='ProofingStatus', max_length=50)  
    holdbyproduction = models.IntegerField(db_column='HoldByProduction')  
    productionholdreason = models.CharField(db_column='ProductionHoldReason', max_length=100)  
    stockallocation = models.CharField(db_column='StockAllocation', max_length=2000)  
    invoiceqty = models.FloatField(db_column='InvoiceQty', blank=True, null=True)  
    constatus = models.CharField(db_column='ConStatus', max_length=200, blank=True, null=True)  
    lastupdatedon = models.DateTimeField(db_column='LastUpdatedOn', blank=True, null=True)  
    noofjobcardscreated = models.IntegerField(db_column='NoOfJobCardsCreated', blank=True, null=True)  
    templateid = models.CharField(db_column='TemplateID', max_length=20)  
    rateinthousand = models.FloatField(db_column='RateInThousand')  
    additionaltax = models.FloatField(db_column='AdditionalTax')  
    receivedamount = models.FloatField(db_column='ReceivedAmount')  
    discount = models.FloatField(db_column='Discount')  
    projectedwoid = models.CharField(db_column='ProjectedWOID', max_length=100)  
    projectedwoqty = models.CharField(db_column='ProjectedWOQTY', max_length=100)  
    pono = models.CharField(db_column='PONo', max_length=500)  
    poinovieqty = models.CharField(db_column='POInovieQty', max_length=500)  
    releaseforplnning = models.IntegerField(db_column='ReleaseForPlnning')  
    printsougthdate = models.DateField(db_column='PrintSougthDate')  
    printplandate = models.DateField(db_column='PrintPlanDate')  
    rateunit = models.CharField(db_column='RateUnit', max_length=100, blank=True, null=True)  
    ct3id = models.IntegerField()
    extra1 = models.CharField(db_column='Extra1', max_length=100)  
    extra2 = models.CharField(db_column='Extra2', max_length=100)  
    extra3 = models.CharField(db_column='Extra3', max_length=100)  
    extra4 = models.CharField(db_column='Extra4', max_length=100)  
    extra5 = models.CharField(db_column='Extra5', max_length=100)  
    planpriority = models.IntegerField(db_column='PlanPriority')  
    lotidval = models.CharField(max_length=30, blank=True, null=True)
    actualrate = models.FloatField()
    processcharge = models.CharField(db_column='ProcessCharge', max_length=50)  
    prstatus = models.IntegerField(db_column='PRStatus')  
    expdeldate = models.DateField(db_column='ExpDeldate')  
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  
    artworkreceive = models.IntegerField(db_column='Artworkreceive')  
    planningclose = models.IntegerField(db_column='Planningclose')  
    poqty = models.IntegerField(db_column='POQty')  
    motherjobno = models.CharField(db_column='MotherJobNo', max_length=20)  
    motherfpid = models.CharField(db_column='MotherFPID', max_length=10)  
    maxdispatchqty = models.IntegerField(db_column='MaxDispatchQty')  
    closedate = models.DateTimeField(db_column='CloseDate')  
    closeby = models.CharField(db_column='CloseBy', max_length=10, blank=True, null=True)  
    closereason = models.TextField(db_column='CloseReason', blank=True, null=True)  
    expdeldate_modify = models.DateField(db_column='ExpDeldate_Modify')  
    gpnqty = models.IntegerField(db_column='GPNQty')  
    docnotion = models.IntegerField(db_column='DocNotion')  
    reprintqty = models.IntegerField()
    salesreturnqty = models.IntegerField()
    processing = models.CharField(db_column='Processing', max_length=45, blank=True, null=True)  
    wochecklistapproval = models.IntegerField(db_column='WoCheckListApproval')  
    wochecklistremarks = models.CharField(db_column='WoCheckListRemarks', max_length=250)  
    wocheckedby = models.CharField(db_column='WoCheckedBy', max_length=10)  
    wocheckeddatetime = models.DateTimeField(db_column='WoCheckedDateTime')  
    billaddchk = models.IntegerField(db_column='BillAddChk')  
    shipaddchk = models.IntegerField(db_column='ShipAddChk')  
    poqtychk = models.IntegerField(db_column='POQtyChk')  
    poratechk = models.IntegerField(db_column='PORateChk')  
    taxchk = models.IntegerField(db_column='TaxChk')  
    openreason = models.CharField(db_column='OpenReason', max_length=250)  
    openby = models.CharField(db_column='OpenBy', max_length=10)  
    opendate = models.DateTimeField(db_column='OpenDate')  
    wrmcid = models.IntegerField(db_column='wrmcID')  
    embose = models.CharField(max_length=50)
    jobtype = models.CharField(db_column='JobType', max_length=50)  
    punch = models.CharField(db_column='Punch', max_length=50)  
    foilblock = models.CharField(db_column='FoilBlock', max_length=50)  

    class Meta:
        managed = False
        db_table = 'item_WODetail'
        unique_together = (('jobno', 'docnotion'),)


class Companydelqtydate(models.Model):
    recordid_old = models.CharField(db_column='RecordID_OLD', max_length=30)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    qtytodeliver = models.FloatField(db_column='QtyToDeliver')  
    lastdeliverydate = models.DateTimeField(db_column='LastDeliveryDate')  
    delrecordid = models.CharField(db_column='DelRecordID', max_length=10)  
    woid = models.CharField(db_column='WOID', max_length=30)  
    clientid = models.CharField(db_column='ClientID', max_length=10)  
    itemid = models.CharField(db_column='ItemID', max_length=10)  
    specid = models.CharField(db_column='SpecID', max_length=10)  
    schdeliverydate = models.DateTimeField(db_column='SchDeliveryDate')  
    qtydelivered = models.FloatField(db_column='QtyDelivered')  
    lastdespatchdate = models.DateTimeField(db_column='LastDespatchDate')  
    deleyreasonid = models.IntegerField()
    jobno = models.CharField(db_column='JobNo', max_length=20)  
    rowno = models.IntegerField(db_column='Rowno')  
    itemcode_locationwise = models.CharField(db_column='ItemCode_LocationWise', max_length=50)  
    docnotion = models.IntegerField(db_column='DocNotion')  
    comp_main_woid = models.CharField(db_column='Comp_Main_WOID', max_length=30)  
    motherjobno = models.CharField(db_column='MotherJobNo', max_length=30)  
    recordid = models.AutoField(db_column='RecordID', primary_key=True)  
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  
    comp_main_recordid = models.IntegerField(db_column='Comp_main_RecordID', blank=True, null=True)  
    billaddressid = models.CharField(db_column='BillAddressID', max_length=20)  
    deladdressdesc = models.TextField(db_column='DelAddressDesc', blank=True, null=True)  
    billaddressdesc = models.TextField(db_column='BillAddressDesc', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'CompanyDelQtyDate'




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
