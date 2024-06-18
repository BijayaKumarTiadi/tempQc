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
