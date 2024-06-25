# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ItemWomaster(models.Model):
    awoid = models.AutoField(db_column='AWOID', primary_key=True)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  # Field name made lowercase.
    woid = models.CharField(db_column='WOID', max_length=30)  # Field name made lowercase.
    sprefix = models.CharField(db_column='SPrefix', max_length=15)  # Field name made lowercase.
    swono = models.CharField(db_column='SWONo', max_length=10)  # Field name made lowercase.
    ssufix = models.CharField(db_column='SSufix', max_length=2)  # Field name made lowercase.
    wodate = models.DateTimeField(db_column='WODate', blank=True, null=True)  # Field name made lowercase.
    postatus = models.CharField(db_column='POStatus', max_length=100)  # Field name made lowercase.
    wono = models.CharField(db_column='WONo', max_length=30, blank=True, null=True)  # Field name made lowercase.
    podate = models.DateTimeField(db_column='PODate')  # Field name made lowercase.
    clientid = models.CharField(db_column='ClientId', max_length=10, blank=True, null=True)  # Field name made lowercase.
    execid = models.CharField(db_column='ExecId', max_length=20)  # Field name made lowercase.
    orderedby = models.CharField(db_column='OrderedBy', max_length=45, blank=True, null=True)  # Field name made lowercase.
    paymentday = models.CharField(db_column='PaymentDay', max_length=50)  # Field name made lowercase.
    paymenttype = models.CharField(db_column='PaymentType', max_length=100)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive')  # Field name made lowercase.
    auid = models.CharField(db_column='AUID', max_length=10)  # Field name made lowercase.
    adatetime = models.CharField(db_column='ADateTime', max_length=45)  # Field name made lowercase.
    muid = models.CharField(db_column='MUID', max_length=10)  # Field name made lowercase.
    mdatetime = models.CharField(db_column='MDateTime', max_length=45)  # Field name made lowercase.
    duid = models.CharField(db_column='DUID', max_length=10)  # Field name made lowercase.
    ddatetime = models.CharField(db_column='DDateTime', max_length=45)  # Field name made lowercase.
    filelocation = models.CharField(db_column='FileLocation', max_length=225)  # Field name made lowercase.
    hdpe = models.PositiveIntegerField(db_column='HDPE')  # Field name made lowercase.
    proofingchk = models.PositiveIntegerField(db_column='ProofingCHK')  # Field name made lowercase.
    unique_projectionno = models.CharField(db_column='Unique_ProjectionNo', max_length=100)  # Field name made lowercase.
    poreceivedate = models.DateTimeField(db_column='POReceiveDate')  # Field name made lowercase.
    comp_main_woid = models.CharField(db_column='Comp_Main_WOID', max_length=30)  # Field name made lowercase.
    motherfpid = models.CharField(db_column='MotherFPID', max_length=10)  # Field name made lowercase.
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  # Field name made lowercase.
    docnotion = models.IntegerField(db_column='DocNotion')  # Field name made lowercase.
    freightapplicable = models.PositiveIntegerField(db_column='FreightApplicable')  # Field name made lowercase.
    porecdate = models.CharField(db_column='PORecDate', max_length=100)  # Field name made lowercase.
    artworkdate = models.CharField(db_column='ArtWorkDate', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item_womaster'
        unique_together = (('awoid', 'woid', 'docnotion'),)


class ItemWodetail(models.Model):
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  # Field name made lowercase.
    woid = models.CharField(db_column='WOId', max_length=30)  # Field name made lowercase.
    jobno = models.CharField(db_column='JobNo', primary_key=True, max_length=20)  # Field name made lowercase.
    rowno = models.IntegerField(db_column='Rowno')  # Field name made lowercase.
    estimateno = models.CharField(db_column='EstimateNo', max_length=30)  # Field name made lowercase.
    itemid = models.CharField(db_column='ItemID', max_length=10)  # Field name made lowercase.
    itemcode = models.CharField(db_column='ItemCode', max_length=40)  # Field name made lowercase.
    codeno = models.CharField(db_column='CodeNo', max_length=45)  # Field name made lowercase.
    itemdesc = models.CharField(db_column='ItemDesc', max_length=1000)  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity')  # Field name made lowercase.
    percentvar = models.FloatField(db_column='PercentVar')  # Field name made lowercase.
    qtyplus = models.FloatField(db_column='QtyPlus')  # Field name made lowercase.
    qtyminus = models.FloatField(db_column='QtyMinus')  # Field name made lowercase.
    unitid = models.CharField(db_column='UnitID', max_length=10)  # Field name made lowercase.
    rate = models.FloatField(db_column='Rate')  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount')  # Field name made lowercase.
    packing = models.FloatField(db_column='Packing')  # Field name made lowercase.
    freight = models.FloatField(db_column='Freight')  # Field name made lowercase.
    insurance = models.FloatField(db_column='Insurance')  # Field name made lowercase.
    specification = models.CharField(db_column='Specification', max_length=10)  # Field name made lowercase.
    ref = models.CharField(max_length=45)
    color = models.CharField(max_length=45)
    cp = models.CharField(db_column='CP', max_length=1, blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks')  # Field name made lowercase.
    remarkinv = models.TextField(db_column='RemarkInv')  # Field name made lowercase.
    qtydispatched = models.FloatField(db_column='QtyDispatched')  # Field name made lowercase.
    modeoftrans = models.CharField(db_column='ModeOfTrans', max_length=50)  # Field name made lowercase.
    fgtype = models.CharField(max_length=30)
    isactive = models.IntegerField(db_column='IsActive')  # Field name made lowercase.
    transfer_wo = models.IntegerField()
    chrgetype1 = models.CharField(max_length=45)
    chargevalue1 = models.CharField(max_length=45)
    chrgetype2 = models.CharField(max_length=45)
    chargevalue2 = models.CharField(max_length=45)
    chrgetype3 = models.CharField(max_length=45)
    chargevalue3 = models.CharField(max_length=45)
    totjobcardqty = models.IntegerField(db_column='Totjobcardqty')  # Field name made lowercase.
    dontshowforjc = models.IntegerField(db_column='DontShowForJc', blank=True, null=True)  # Field name made lowercase.
    hold = models.IntegerField(db_column='Hold')  # Field name made lowercase.
    clstatus = models.PositiveIntegerField(db_column='CLStatus')  # Field name made lowercase.
    approved = models.FloatField(db_column='Approved')  # Field name made lowercase.
    approvedby = models.CharField(db_column='ApprovedBy', max_length=45)  # Field name made lowercase.
    approvaldate = models.DateTimeField(db_column='ApprovalDate')  # Field name made lowercase.
    appremarks = models.CharField(db_column='AppRemarks', max_length=45)  # Field name made lowercase.
    deldate = models.CharField(db_column='DelDate', max_length=30)  # Field name made lowercase.
    recordid = models.CharField(db_column='RecordID', max_length=30)  # Field name made lowercase.
    diladd = models.TextField(db_column='DilAdd')  # Field name made lowercase.
    delschedule = models.TextField(db_column='DelSchedule')  # Field name made lowercase.
    artworkno = models.CharField(db_column='ArtWorkNo', max_length=45)  # Field name made lowercase.
    addressid = models.CharField(db_column='AddressID', max_length=250)  # Field name made lowercase.
    addqty = models.CharField(db_column='AddQty', max_length=250)  # Field name made lowercase.
    shadecardid = models.CharField(db_column='ShadeCardID', max_length=45)  # Field name made lowercase.
    commitdt = models.CharField(db_column='CommitDt', max_length=20)  # Field name made lowercase.
    commitschedule = models.TextField(db_column='CommitSchedule')  # Field name made lowercase.
    exciseduty = models.FloatField(db_column='ExciseDuty')  # Field name made lowercase.
    edcess = models.FloatField(db_column='EDCESS')  # Field name made lowercase.
    shecess = models.FloatField(db_column='SHECESS')  # Field name made lowercase.
    vat = models.FloatField(db_column='VAT')  # Field name made lowercase.
    cst = models.FloatField(db_column='CST')  # Field name made lowercase.
    servicetax = models.FloatField(db_column='ServiceTax')  # Field name made lowercase.
    extracol = models.FloatField(db_column='ExtraCol')  # Field name made lowercase.
    salestype = models.CharField(db_column='SalesType', max_length=50)  # Field name made lowercase.
    internaljobno = models.CharField(db_column='InternalJobNo', max_length=50)  # Field name made lowercase.
    internaljobdate = models.CharField(db_column='InternalJobDate', max_length=50)  # Field name made lowercase.
    internalestimateno = models.CharField(db_column='InternalEstimateNo', max_length=50)  # Field name made lowercase.
    internalestimatedate = models.CharField(db_column='InternalEstimateDate', max_length=50)  # Field name made lowercase.
    proofingstatus = models.CharField(db_column='ProofingStatus', max_length=50)  # Field name made lowercase.
    holdbyproduction = models.IntegerField(db_column='HoldByProduction')  # Field name made lowercase.
    productionholdreason = models.CharField(db_column='ProductionHoldReason', max_length=100)  # Field name made lowercase.
    stockallocation = models.CharField(db_column='StockAllocation', max_length=2000)  # Field name made lowercase.
    invoiceqty = models.FloatField(db_column='InvoiceQty', blank=True, null=True)  # Field name made lowercase.
    constatus = models.CharField(db_column='ConStatus', max_length=200, blank=True, null=True)  # Field name made lowercase.
    lastupdatedon = models.DateTimeField(db_column='LastUpdatedOn', blank=True, null=True)  # Field name made lowercase.
    noofjobcardscreated = models.IntegerField(db_column='NoOfJobCardsCreated', blank=True, null=True)  # Field name made lowercase.
    templateid = models.CharField(db_column='TemplateID', max_length=20)  # Field name made lowercase.
    rateinthousand = models.FloatField(db_column='RateInThousand')  # Field name made lowercase.
    additionaltax = models.FloatField(db_column='AdditionalTax')  # Field name made lowercase.
    receivedamount = models.FloatField(db_column='ReceivedAmount')  # Field name made lowercase.
    discount = models.FloatField(db_column='Discount')  # Field name made lowercase.
    projectedwoid = models.CharField(db_column='ProjectedWOID', max_length=100)  # Field name made lowercase.
    projectedwoqty = models.CharField(db_column='ProjectedWOQTY', max_length=100)  # Field name made lowercase.
    pono = models.CharField(db_column='PONo', max_length=500)  # Field name made lowercase.
    poinovieqty = models.CharField(db_column='POInovieQty', max_length=500)  # Field name made lowercase.
    releaseforplnning = models.IntegerField(db_column='ReleaseForPlnning')  # Field name made lowercase.
    printsougthdate = models.DateField(db_column='PrintSougthDate')  # Field name made lowercase.
    printplandate = models.DateField(db_column='PrintPlanDate')  # Field name made lowercase.
    rateunit = models.CharField(db_column='RateUnit', max_length=100, blank=True, null=True)  # Field name made lowercase.
    ct3id = models.IntegerField()
    extra1 = models.CharField(db_column='Extra1', max_length=100)  # Field name made lowercase.
    extra2 = models.CharField(db_column='Extra2', max_length=100)  # Field name made lowercase.
    extra3 = models.CharField(db_column='Extra3', max_length=100)  # Field name made lowercase.
    extra4 = models.CharField(db_column='Extra4', max_length=100)  # Field name made lowercase.
    extra5 = models.CharField(db_column='Extra5', max_length=100)  # Field name made lowercase.
    planpriority = models.IntegerField(db_column='PlanPriority')  # Field name made lowercase.
    lotidval = models.CharField(max_length=30, blank=True, null=True)
    actualrate = models.FloatField()
    processcharge = models.CharField(db_column='ProcessCharge', max_length=50)  # Field name made lowercase.
    prstatus = models.IntegerField(db_column='PRStatus')  # Field name made lowercase.
    expdeldate = models.DateField(db_column='ExpDeldate')  # Field name made lowercase.
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  # Field name made lowercase.
    artworkreceive = models.IntegerField(db_column='Artworkreceive')  # Field name made lowercase.
    planningclose = models.IntegerField(db_column='Planningclose')  # Field name made lowercase.
    poqty = models.IntegerField(db_column='POQty')  # Field name made lowercase.
    motherjobno = models.CharField(db_column='MotherJobNo', max_length=20)  # Field name made lowercase.
    motherfpid = models.CharField(db_column='MotherFPID', max_length=10)  # Field name made lowercase.
    maxdispatchqty = models.IntegerField(db_column='MaxDispatchQty')  # Field name made lowercase.
    closedate = models.DateTimeField(db_column='CloseDate')  # Field name made lowercase.
    closeby = models.CharField(db_column='CloseBy', max_length=10, blank=True, null=True)  # Field name made lowercase.
    closereason = models.TextField(db_column='CloseReason', blank=True, null=True)  # Field name made lowercase.
    expdeldate_modify = models.DateField(db_column='ExpDeldate_Modify')  # Field name made lowercase.
    gpnqty = models.IntegerField(db_column='GPNQty')  # Field name made lowercase.
    docnotion = models.IntegerField(db_column='DocNotion')  # Field name made lowercase.
    reprintqty = models.IntegerField()
    salesreturnqty = models.IntegerField()
    processing = models.CharField(db_column='Processing', max_length=45, blank=True, null=True)  # Field name made lowercase.
    wochecklistapproval = models.IntegerField(db_column='WoCheckListApproval')  # Field name made lowercase.
    wochecklistremarks = models.CharField(db_column='WoCheckListRemarks', max_length=250)  # Field name made lowercase.
    wocheckedby = models.CharField(db_column='WoCheckedBy', max_length=10)  # Field name made lowercase.
    wocheckeddatetime = models.DateTimeField(db_column='WoCheckedDateTime')  # Field name made lowercase.
    billaddchk = models.IntegerField(db_column='BillAddChk')  # Field name made lowercase.
    shipaddchk = models.IntegerField(db_column='ShipAddChk')  # Field name made lowercase.
    poqtychk = models.IntegerField(db_column='POQtyChk')  # Field name made lowercase.
    poratechk = models.IntegerField(db_column='PORateChk')  # Field name made lowercase.
    taxchk = models.IntegerField(db_column='TaxChk')  # Field name made lowercase.
    openreason = models.CharField(db_column='OpenReason', max_length=250)  # Field name made lowercase.
    openby = models.CharField(db_column='OpenBy', max_length=10)  # Field name made lowercase.
    opendate = models.DateTimeField(db_column='OpenDate')  # Field name made lowercase.
    wrmcid = models.IntegerField(db_column='wrmcID')  # Field name made lowercase.
    embose = models.CharField(max_length=50)
    jobtype = models.CharField(db_column='JobType', max_length=50)  # Field name made lowercase.
    punch = models.CharField(db_column='Punch', max_length=50)  # Field name made lowercase.
    foilblock = models.CharField(db_column='FoilBlock', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item_wodetail'
        unique_together = (('jobno', 'docnotion'),)


class Companydelqtydate(models.Model):
    recordid_old = models.CharField(db_column='RecordID_OLD', max_length=30)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  # Field name made lowercase.
    qtytodeliver = models.FloatField(db_column='QtyToDeliver')  # Field name made lowercase.
    lastdeliverydate = models.DateTimeField(db_column='LastDeliveryDate')  # Field name made lowercase.
    delrecordid = models.CharField(db_column='DelRecordID', max_length=10)  # Field name made lowercase.
    woid = models.CharField(db_column='WOID', max_length=30)  # Field name made lowercase.
    clientid = models.CharField(db_column='ClientID', max_length=10)  # Field name made lowercase.
    itemid = models.CharField(db_column='ItemID', max_length=10)  # Field name made lowercase.
    specid = models.CharField(db_column='SpecID', max_length=10)  # Field name made lowercase.
    schdeliverydate = models.DateTimeField(db_column='SchDeliveryDate')  # Field name made lowercase.
    qtydelivered = models.FloatField(db_column='QtyDelivered')  # Field name made lowercase.
    lastdespatchdate = models.DateTimeField(db_column='LastDespatchDate')  # Field name made lowercase.
    deleyreasonid = models.IntegerField()
    jobno = models.CharField(db_column='JobNo', max_length=20)  # Field name made lowercase.
    rowno = models.IntegerField(db_column='Rowno')  # Field name made lowercase.
    itemcode_locationwise = models.CharField(db_column='ItemCode_LocationWise', max_length=50)  # Field name made lowercase.
    docnotion = models.IntegerField(db_column='DocNotion')  # Field name made lowercase.
    comp_main_woid = models.CharField(db_column='Comp_Main_WOID', max_length=30)  # Field name made lowercase.
    motherjobno = models.CharField(db_column='MotherJobNo', max_length=30)  # Field name made lowercase.
    recordid = models.AutoField(db_column='RecordID', primary_key=True)  # Field name made lowercase.
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  # Field name made lowercase.
    comp_main_recordid = models.IntegerField(db_column='Comp_main_RecordID', blank=True, null=True)  # Field name made lowercase.
    billaddressid = models.CharField(db_column='BillAddressID', max_length=20)  # Field name made lowercase.
    deladdressdesc = models.TextField(db_column='DelAddressDesc', blank=True, null=True)  # Field name made lowercase.
    billaddressdesc = models.TextField(db_column='BillAddressDesc', blank=True, null=True)  # Field name made lowercase.
    billingrecordid = models.CharField(db_column='BillingRecordID', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'companydelqtydate'
