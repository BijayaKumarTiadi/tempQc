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


class CompanymasterEx1(models.Model):
    companyid = models.CharField(db_column='CompanyId', max_length=10, blank=True, null=True)  
    cname = models.CharField(db_column='CName', max_length=100, blank=True, null=True)  
    deptpost = models.CharField(db_column='DeptPost', max_length=100, blank=True, null=True)  
    contactno = models.CharField(db_column='ContactNo', max_length=200, blank=True, null=True)  
    mobileno = models.CharField(db_column='MobileNo', max_length=50, blank=True, null=True)  
    faxno = models.CharField(db_column='FaxNo', max_length=50, blank=True, null=True)  
    email = models.CharField(db_column='EMail', max_length=200, blank=True, null=True)  
    address = models.TextField(db_column='Address', blank=True, null=True)  
    city = models.CharField(db_column='City', max_length=50, blank=True, null=True)  
    state = models.CharField(db_column='State', max_length=50, blank=True, null=True)  
    ho = models.PositiveIntegerField(db_column='HO')  
    isactive = models.PositiveIntegerField(db_column='IsActive')  
    detailid = models.CharField(db_column='DetailID', primary_key=True, max_length=10)  
    isemail = models.IntegerField(db_column='IsEmail')  

    class Meta:
        managed = False
        db_table = 'companymaster_ex1'



class ItemFpmasterext(models.Model):
    productid = models.CharField(db_column='ProductID', primary_key=True, max_length=10)  
    groupid = models.CharField(db_column='GroupID', max_length=10)  
    description = models.CharField(db_column='Description', max_length=500)  
    manufacturer = models.CharField(db_column='Manufacturer', max_length=50)  
    quality = models.CharField(db_column='Quality', max_length=50)  
    purchaserate = models.FloatField(db_column='PurchaseRate')  
    uom = models.CharField(db_column='UOM', max_length=10)  
    packingunit = models.CharField(db_column='PackingUnit', max_length=20)  
    packaging = models.CharField(db_column='Packaging', max_length=10)  
    rol = models.FloatField(db_column='ROL')  
    roq = models.FloatField(db_column='ROQ')  
    mql = models.FloatField(db_column='MQL')  
    openingstock = models.FloatField(db_column='OpeningStock')  
    openingstockvalue = models.FloatField(db_column='OpeningStockValue')  
    closingstock = models.FloatField(db_column='ClosingStock')  
    lastpurchaseqty = models.FloatField(db_column='LastPurchaseQty')  
    lastpurchaserate = models.FloatField(db_column='LastPurchaseRate')  
    avgpurchaserate = models.FloatField(db_column='AvgPurchaseRate')  
    lastpurchasedate = models.DateTimeField(db_column='LastPurchaseDate')  
    valuationmethod = models.CharField(db_column='ValuationMethod', max_length=20)  
    isactive = models.PositiveIntegerField(db_column='IsActive')  
    remarks = models.CharField(db_column='Remarks', max_length=100)  
    stdrate = models.FloatField(db_column='StdRate')  
    type = models.CharField(db_column='Type', max_length=2)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    packdetails = models.CharField(db_column='PackDetails', max_length=200)  
    uid = models.CharField(db_column='UID', max_length=10)  
    modvat = models.PositiveIntegerField(db_column='ModVat')  
    iprefix = models.CharField(db_column='IPrefix', max_length=255)  
    qc = models.PositiveIntegerField(db_column='QC')  
    itemcategory = models.CharField(db_column='ItemCategory', max_length=5)  
    acccode = models.CharField(db_column='AccCode', max_length=45)  
    minqty = models.CharField(db_column='MinQty', max_length=11, blank=True, null=True)  
    l = models.CharField(db_column='L', max_length=10, blank=True, null=True)  
    b = models.CharField(db_column='B', max_length=10, blank=True, null=True)  
    h = models.CharField(db_column='H', max_length=10, blank=True, null=True)  
    attfilename = models.CharField(db_column='AttFileName', max_length=100, blank=True, null=True)  
    attimagename = models.CharField(db_column='AttImageName', max_length=100, blank=True, null=True)  
    exedays = models.FloatField(db_column='ExeDays', blank=True, null=True)  
    specialremarks = models.CharField(db_column='SpecialRemarks', max_length=250, blank=True, null=True)  
    otherdiemationdetail = models.CharField(db_column='OtherDiemationDetail', max_length=200, blank=True, null=True)  
    ischecked = models.PositiveIntegerField(db_column='IsChecked')  
    auid = models.CharField(db_column='AUID', max_length=20)  
    adatetime = models.CharField(db_column='Adatetime', max_length=50)  
    muid = models.CharField(db_column='MUID', max_length=20)  
    mdatetime = models.CharField(db_column='MDateTime', max_length=50)  
    supplyfrom = models.CharField(db_column='SupplyFrom', max_length=200)  
    destination = models.CharField(db_column='Destination', max_length=200)  
    forr = models.CharField(db_column='Forr', max_length=100)  
    annualqty = models.CharField(db_column='AnnualQty', max_length=50)  
    lotsize = models.CharField(db_column='LotSize', max_length=50)  
    approvedrate = models.CharField(db_column='ApprovedRate', max_length=50)  
    descriptionalias = models.CharField(db_column='DescriptionAlias', max_length=500)  
    job_lpi = models.CharField(db_column='Job_LPI', max_length=45)  
    blanket_no = models.CharField(db_column='Blanket_No', max_length=100)  
    wastagetemplateid = models.IntegerField(db_column='WastageTemplateID')  
    flap = models.CharField(db_column='Flap', max_length=10)  
    cartonweight = models.FloatField(db_column='CartonWeight')  
    estimaterecid = models.CharField(db_column='EstimateRecID', max_length=10)  
    collarflap = models.IntegerField(db_column='CollarFlap')  
    productcategory = models.IntegerField(db_column='ProductCategory')  
    excessvarince = models.CharField(db_column='Excessvarince', max_length=50)  
    opensize = models.CharField(db_column='OpenSize', max_length=100)  
    foldedsize = models.CharField(db_column='FoldedSize', max_length=100)  
    newrepeat = models.CharField(db_column='NewRepeat', max_length=20)  
    onlycorrugated = models.IntegerField(db_column='OnlyCorrugated')  
    jobtype = models.CharField(db_column='JobType', max_length=50)  
    sidepast = models.FloatField(db_column='SidePast')  
    otherdimension1 = models.FloatField(db_column='OtherDimension1')  
    otherdimension2 = models.FloatField(db_column='OtherDimension2')  
    otherdimension3 = models.FloatField(db_column='OtherDimension3')  
    flapsidegutter = models.FloatField(db_column='FlapSideGutter')  
    pastsidegutter = models.FloatField(db_column='PastSideGutter')  
    number_2dcode = models.IntegerField(db_column='2dcode')  # Field renamed because it wasn't a valid Python identifier.
    ref_itemid = models.CharField(db_column='Ref_ItemID', max_length=10)  
    isassembly = models.IntegerField(db_column='IsAssembly')  
    slength = models.FloatField(db_column='SLength')  
    sbreadth = models.FloatField(db_column='SBreadth')  
    sheight = models.FloatField(db_column='SHeight')  
    pershipperweight = models.FloatField(db_column='PerShipperWeight')  
    pershippercarton = models.FloatField(db_column='PerShipperCarton')  
    createddate = models.DateField(db_column='CreatedDate')  
    fulloutsource = models.IntegerField(db_column='FullOutSource')  
    marketing_approved = models.IntegerField(db_column='Marketing_Approved')  
    production_approved = models.IntegerField(db_column='Production_Approved')  
    qc_approved = models.IntegerField(db_column='QC_Approved')  
    bangladesh_job = models.IntegerField(db_column='BANGLADESH_JOB')  

    class Meta:
        managed = False
        db_table = 'item_fpmasterext'


class ItemUnitMaster(models.Model):
    unitid = models.CharField(db_column='UnitID', primary_key=True, max_length=10)  
    unitname = models.CharField(db_column='UnitName', max_length=30, blank=True, null=True)  
    isactive = models.PositiveIntegerField(db_column='IsActive')  

    class Meta:
        managed = False
        db_table = 'item_unit_master'


class ItemGroupMaster(models.Model):
    groupid = models.CharField(db_column='GroupID', max_length=10)  
    groupname = models.CharField(db_column='GroupName', max_length=50, blank=True, null=True)  
    isactive = models.PositiveIntegerField(db_column='IsActive')  
    h = models.PositiveIntegerField(db_column='H')  
    gprefix = models.CharField(db_column='GPrefix', max_length=10)  
    current_no = models.CharField(db_column='Current_no', max_length=20)  
    gbasicdiscount = models.CharField(db_column='GBasicDiscount', max_length=10)  
    gexcise = models.CharField(db_column='GExcise', max_length=10)  
    garcess = models.CharField(db_column='GARCess', max_length=10)  
    geducess = models.CharField(db_column='GEduCess', max_length=10)  
    gshecess = models.CharField(db_column='GSheCess', max_length=10)  
    ginsurance = models.CharField(db_column='GInsurance', max_length=10)  
    gcommision = models.CharField(db_column='GCommision', max_length=10)  
    ginterest = models.CharField(db_column='GInterest', max_length=10)  
    gfreight = models.CharField(db_column='GFreight', max_length=10)  
    gpkg_fwd = models.CharField(db_column='GPkg_Fwd', max_length=10)  
    gvat = models.CharField(db_column='GVat', max_length=10)  
    gaddlvat = models.CharField(db_column='GAddlVat', max_length=10)  
    gtarrifadd = models.CharField(db_column='GTarrifAdd', max_length=10)  
    typesofgoods = models.CharField(db_column='TypesOfGoods', max_length=50)  
    lastitemcode = models.PositiveIntegerField(db_column='LastItemCode')  
    category = models.CharField(max_length=10)
    budgetper = models.FloatField()
    directpo = models.IntegerField(db_column='Directpo')  
    groupname_for_tally = models.CharField(db_column='GroupName_for_Tally', max_length=100)  

    class Meta:
        managed = False
        db_table = 'item_group_master'


class ItemClass(models.Model):
    classid = models.CharField(db_column='classID', primary_key=True, max_length=10)  
    classname = models.CharField(db_column='className', max_length=500)  
    isactive = models.PositiveIntegerField(db_column='IsActive')  
    cexcise = models.CharField(db_column='CExcise', max_length=10)  
    cedcess = models.CharField(db_column='CEDCess', max_length=10)  
    cshecess = models.CharField(db_column='CSHECess', max_length=10)  
    cvat = models.CharField(db_column='CVAT', max_length=10)  
    ctarrifadd = models.CharField(db_column='CTarrifAdd', max_length=10)  
    excisedetailid = models.IntegerField(db_column='ExciseDetailId')  
    igst = models.DecimalField(db_column='IGST', max_digits=5, decimal_places=2)  
    cgst = models.DecimalField(db_column='CGST', max_digits=5, decimal_places=2)  
    sgst = models.DecimalField(db_column='SGST', max_digits=5, decimal_places=2)  
    lclassid = models.CharField(db_column='LClassid', max_length=10)  
    iclassid = models.CharField(db_column='IClassid', max_length=10)  

    class Meta:
        managed = False
        db_table = 'item_class'


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
        db_table = 'item_womaster'
        unique_together = (('awoid', 'woid', 'docnotion'),)


class ItemWodetail(models.Model):
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    woid = models.CharField(db_column='WOId', max_length=30)  
    jobno = models.CharField(db_column='JobNo', primary_key=True, max_length=20)  
    rowno = models.IntegerField(db_column='Rowno', default=0)  
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
    packing = models.FloatField(db_column='Packing',default=0)  
    freight = models.FloatField(db_column='Freight')  
    insurance = models.FloatField(db_column='Insurance', default=0)  
    specification = models.CharField(db_column='Specification', max_length=10)  
    ref = models.CharField(max_length=45)
    color = models.CharField(max_length=45)
    cp = models.CharField(db_column='CP', max_length=1, blank=True, null=True)  
    remarks = models.TextField(db_column='Remarks')  
    remarkinv = models.TextField(db_column='RemarkInv')  
    qtydispatched = models.FloatField(db_column='QtyDispatched', default=0.00000)  
    modeoftrans = models.CharField(db_column='ModeOfTrans', max_length=50)  
    fgtype = models.CharField(max_length=30)
    isactive = models.IntegerField(db_column='IsActive', default=0)  
    transfer_wo = models.IntegerField(default=0)
    chrgetype1 = models.CharField(max_length=45)
    chargevalue1 = models.CharField(max_length=45)
    chrgetype2 = models.CharField(max_length=45)
    chargevalue2 = models.CharField(max_length=45)
    chrgetype3 = models.CharField(max_length=45)
    chargevalue3 = models.CharField(max_length=45)
    totjobcardqty = models.IntegerField(db_column='Totjobcardqty', default=0)  
    dontshowforjc = models.IntegerField(db_column='DontShowForJc',default=0, blank=True, null=True)  
    hold = models.IntegerField(db_column='Hold',default=0)  
    clstatus = models.PositiveIntegerField(db_column='CLStatus', default=0)  
    approved = models.FloatField(db_column='Approved', default=0.00)  
    approvedby = models.CharField(db_column='ApprovedBy', max_length=45)  
    approvaldate = models.DateTimeField(db_column='ApprovalDate', default="1900-12-12 20:20:20")  
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
    exciseduty = models.FloatField(db_column='ExciseDuty', default=0)  
    edcess = models.FloatField(db_column='EDCESS', default=0)  
    shecess = models.FloatField(db_column='SHECESS', default=0)  
    vat = models.FloatField(db_column='VAT', default=0)  
    cst = models.FloatField(db_column='CST', default=0)  
    servicetax = models.FloatField(db_column='ServiceTax', default=0)  
    extracol = models.FloatField(db_column='ExtraCol', default=0)  
    salestype = models.CharField(db_column='SalesType', max_length=50)  
    internaljobno = models.CharField(db_column='InternalJobNo', max_length=50)  
    internaljobdate = models.CharField(db_column='InternalJobDate', max_length=50)  
    internalestimateno = models.CharField(db_column='InternalEstimateNo', max_length=50)  
    internalestimatedate = models.CharField(db_column='InternalEstimateDate', max_length=50)  
    proofingstatus = models.CharField(db_column='ProofingStatus', max_length=50)  
    holdbyproduction = models.IntegerField(db_column='HoldByProduction', default=0)  
    productionholdreason = models.CharField(db_column='ProductionHoldReason', max_length=100)  
    stockallocation = models.CharField(db_column='StockAllocation', max_length=2000)  
    invoiceqty = models.FloatField(db_column='InvoiceQty', blank=True, null=True)  
    constatus = models.CharField(db_column='ConStatus', max_length=200, blank=True, null=True)  
    lastupdatedon = models.DateTimeField(db_column='LastUpdatedOn', blank=True, null=True)  
    noofjobcardscreated = models.IntegerField(db_column='NoOfJobCardsCreated', blank=True, null=True)  
    templateid = models.CharField(db_column='TemplateID', max_length=20)  
    rateinthousand = models.FloatField(db_column='RateInThousand')  
    additionaltax = models.FloatField(db_column='AdditionalTax', default=0)  
    receivedamount = models.FloatField(db_column='ReceivedAmount', default=0.0000)  
    discount = models.FloatField(db_column='Discount', default=0.00)  
    projectedwoid = models.CharField(db_column='ProjectedWOID', max_length=100)  
    projectedwoqty = models.CharField(db_column='ProjectedWOQTY', max_length=100)  
    pono = models.CharField(db_column='PONo', max_length=500)  
    poinovieqty = models.CharField(db_column='POInovieQty', max_length=500)  
    releaseforplnning = models.IntegerField(db_column='ReleaseForPlnning', default=0)  
    printsougthdate = models.DateField(db_column='PrintSougthDate', default="2060-01-01")  
    printplandate = models.DateField(db_column='PrintPlanDate', default="2060-01-01")  
    rateunit = models.CharField(db_column='RateUnit', max_length=100, blank=True, null=True)  
    ct3id = models.IntegerField(default=0)
    extra1 = models.CharField(db_column='Extra1', max_length=100)  
    extra2 = models.CharField(db_column='Extra2', max_length=100)  
    extra3 = models.CharField(db_column='Extra3', max_length=100)  
    extra4 = models.CharField(db_column='Extra4', max_length=100)  
    extra5 = models.CharField(db_column='Extra5', max_length=100)  
    planpriority = models.IntegerField(db_column='PlanPriority', default=0)  
    lotidval = models.CharField(max_length=30, blank=True, null=True)
    actualrate = models.FloatField()
    processcharge = models.CharField(db_column='ProcessCharge', max_length=50)  
    prstatus = models.IntegerField(db_column='PRStatus', default=0)  
    expdeldate = models.DateField(db_column='ExpDeldate', default="2060-01-01")  
    componentwo = models.CharField(db_column='ComponentWO', max_length=5)  
    artworkreceive = models.IntegerField(db_column='Artworkreceive',default=0)  
    planningclose = models.IntegerField(db_column='Planningclose', default=0)  
    poqty = models.IntegerField(db_column='POQty', default=0)  
    motherjobno = models.CharField(db_column='MotherJobNo', max_length=20)  
    motherfpid = models.CharField(db_column='MotherFPID', max_length=10)  
    maxdispatchqty = models.IntegerField(db_column='MaxDispatchQty', default=0)  
    closedate = models.DateTimeField(db_column='CloseDate')  
    closeby = models.CharField(db_column='CloseBy', max_length=10, blank=True, null=True)  
    closereason = models.TextField(db_column='CloseReason', blank=True, null=True)  
    expdeldate_modify = models.DateField(db_column='ExpDeldate_Modify', default="2060-01-01")  
    gpnqty = models.IntegerField(db_column='GPNQty', default=0)  
    docnotion = models.IntegerField(db_column='DocNotion')  
    reprintqty = models.IntegerField(default=0)
    salesreturnqty = models.IntegerField(default=0)
    processing = models.CharField(db_column='Processing', max_length=45, blank=True, null=True)  
    wochecklistapproval = models.IntegerField(db_column='WoCheckListApproval', default=0)  
    wochecklistremarks = models.CharField(db_column='WoCheckListRemarks', max_length=250)  
    wocheckedby = models.CharField(db_column='WoCheckedBy', max_length=10)  
    wocheckeddatetime = models.DateTimeField(db_column='WoCheckedDateTime', default="1970-01-01 00:00:00")  
    billaddchk = models.IntegerField(db_column='BillAddChk', default=0)  
    shipaddchk = models.IntegerField(db_column='ShipAddChk', default=0)  
    poqtychk = models.IntegerField(db_column='POQtyChk', default=0)  
    poratechk = models.IntegerField(db_column='PORateChk', default=0)  
    taxchk = models.IntegerField(db_column='TaxChk', default=0)  
    openreason = models.CharField(db_column='OpenReason', max_length=250)  
    openby = models.CharField(db_column='OpenBy', max_length=10)  
    opendate = models.DateTimeField(db_column='OpenDate', default="2060-01-01 00:00:00")  
    wrmcid = models.IntegerField(db_column='wrmcID', default=0)  
    embose = models.CharField(max_length=50)
    jobtype = models.CharField(db_column='JobType', max_length=50)  
    punch = models.CharField(db_column='Punch', max_length=50)  
    foilblock = models.CharField(db_column='FoilBlock', max_length=50)  

    class Meta:
        managed = False
        db_table = 'item_wodetail'
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
    qtydelivered = models.FloatField(db_column='QtyDelivered', default=0.00)  
    lastdespatchdate = models.DateTimeField(db_column='LastDespatchDate', default="1900-01-01 00:00:00")  
    deleyreasonid = models.IntegerField(default=0)
    jobno = models.CharField(db_column='JobNo', max_length=20)  
    rowno = models.IntegerField(db_column='Rowno' , default=0)  
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
    billingrecordid = models.CharField(db_column='BillingRecordID', max_length=10)  

    class Meta:
        managed = False
        db_table = 'companydelqtydate'

class ProductCategoryMaster(models.Model):
    pcategoryid = models.IntegerField(db_column='PCategoryid', primary_key=True)
    particular = models.CharField(db_column='Particular', max_length=100)
    isactive = models.IntegerField(db_column='Isactive')

    class Meta:
        managed = False
        db_table = 'product_category_master'


class ItemPiMaster(models.Model):
    invid = models.AutoField(db_column='INVID', primary_key=True)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    docid = models.CharField(db_column='DOCID', max_length=30)  
    sprefix = models.CharField(db_column='SPrefix', max_length=15)  
    invno = models.CharField(db_column='INVNO', max_length=10)  
    ssufix = models.CharField(db_column='SSufix', max_length=2, blank=True, null=True, default="")  
    invdate = models.DateTimeField(db_column='INVDate', blank=True, null=True)  
    pono = models.CharField(db_column='PONO', max_length=30, blank=True, null=True)  
    podate = models.DateTimeField(db_column='PODate')  
    clientid = models.CharField(db_column='ClientId', max_length=10)  
    execid = models.CharField(db_column='ExecId', max_length=20)  
    orderedby = models.CharField(db_column='OrderedBy', max_length=45)  
    shipvia = models.CharField(db_column='Shipvia', max_length=50)  
    paymentday = models.CharField(db_column='PaymentDay', max_length=50)  
    paymenttype = models.CharField(db_column='PaymentType', max_length=100)  
    remarks = models.CharField(db_column='Remarks', max_length=100)  
    isactive = models.IntegerField(db_column='IsActive')  
    auid = models.CharField(db_column='AUID', max_length=10)  
    adatetime = models.CharField(db_column='ADateTime', max_length=45)  
    muid = models.CharField(db_column='MUID', max_length=10)  
    mdatetime = models.CharField(db_column='MDateTime', max_length=45)  
    duid = models.CharField(db_column='DUID', max_length=10)  
    ddatetime = models.CharField(db_column='DDateTime', max_length=45)  
    filelocation = models.CharField(db_column='FileLocation', max_length=225)  
    docnotion = models.IntegerField(db_column='DocNotion')  
    deliveryaddressid = models.CharField(db_column='DeliveryAddressID', max_length=10, blank=True, null=True)  
    deliveryaddress = models.CharField(db_column='Deliveryaddress', max_length=500)  
    taxid = models.IntegerField(db_column='Taxid')  
    terms = models.CharField(db_column='Terms', max_length=100)  
    ratetype = models.CharField(db_column='RateType', max_length=5)  
    basicamount = models.FloatField(db_column='BasicAmount')  
    freight = models.FloatField(db_column='Freight',default=0, blank=True)  
    insurance = models.FloatField(db_column='Insurance')  
    totalamt = models.FloatField(db_column='TotalAmt')  
    seriesid = models.CharField(db_column='SeriesID', max_length=10, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'item_pi_master'
        unique_together = (('invid', 'docid', 'docnotion'),)
