# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ItemFpmasterext(models.Model):
    productid = models.CharField(db_column='ProductID', primary_key=True, max_length=10)  # Field name made lowercase.
    groupid = models.CharField(db_column='GroupID', max_length=10)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500)  # Field name made lowercase.
    manufacturer = models.CharField(db_column='Manufacturer', max_length=50)  # Field name made lowercase.
    quality = models.CharField(db_column='Quality', max_length=50)  # Field name made lowercase.
    purchaserate = models.FloatField(db_column='PurchaseRate')  # Field name made lowercase.
    uom = models.CharField(db_column='UOM', max_length=10)  # Field name made lowercase.
    packingunit = models.CharField(db_column='PackingUnit', max_length=20)  # Field name made lowercase.
    packaging = models.CharField(db_column='Packaging', max_length=10)  # Field name made lowercase.
    rol = models.FloatField(db_column='ROL')  # Field name made lowercase.
    roq = models.FloatField(db_column='ROQ')  # Field name made lowercase.
    mql = models.FloatField(db_column='MQL')  # Field name made lowercase.
    openingstock = models.FloatField(db_column='OpeningStock')  # Field name made lowercase.
    openingstockvalue = models.FloatField(db_column='OpeningStockValue')  # Field name made lowercase.
    closingstock = models.FloatField(db_column='ClosingStock')  # Field name made lowercase.
    lastpurchaseqty = models.FloatField(db_column='LastPurchaseQty')  # Field name made lowercase.
    lastpurchaserate = models.FloatField(db_column='LastPurchaseRate')  # Field name made lowercase.
    avgpurchaserate = models.FloatField(db_column='AvgPurchaseRate')  # Field name made lowercase.
    lastpurchasedate = models.DateTimeField(db_column='LastPurchaseDate')  # Field name made lowercase.
    valuationmethod = models.CharField(db_column='ValuationMethod', max_length=20)  # Field name made lowercase.
    isactive = models.PositiveIntegerField(db_column='IsActive')  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=100)  # Field name made lowercase.
    stdrate = models.FloatField(db_column='StdRate')  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=2)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  # Field name made lowercase.
    packdetails = models.CharField(db_column='PackDetails', max_length=200)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=10)  # Field name made lowercase.
    modvat = models.PositiveIntegerField(db_column='ModVat')  # Field name made lowercase.
    iprefix = models.CharField(db_column='IPrefix', max_length=255)  # Field name made lowercase.
    qc = models.PositiveIntegerField(db_column='QC')  # Field name made lowercase.
    itemcategory = models.CharField(db_column='ItemCategory', max_length=5)  # Field name made lowercase.
    acccode = models.CharField(db_column='AccCode', max_length=45)  # Field name made lowercase.
    minqty = models.CharField(db_column='MinQty', max_length=11, blank=True, null=True)  # Field name made lowercase.
    l = models.CharField(db_column='L', max_length=10, blank=True, null=True)  # Field name made lowercase.
    b = models.CharField(db_column='B', max_length=10, blank=True, null=True)  # Field name made lowercase.
    h = models.CharField(db_column='H', max_length=10, blank=True, null=True)  # Field name made lowercase.
    attfilename = models.CharField(db_column='AttFileName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    attimagename = models.CharField(db_column='AttImageName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    exedays = models.FloatField(db_column='ExeDays', blank=True, null=True)  # Field name made lowercase.
    specialremarks = models.CharField(db_column='SpecialRemarks', max_length=250, blank=True, null=True)  # Field name made lowercase.
    otherdiemationdetail = models.CharField(db_column='OtherDiemationDetail', max_length=200, blank=True, null=True)  # Field name made lowercase.
    ischecked = models.PositiveIntegerField(db_column='IsChecked')  # Field name made lowercase.
    auid = models.CharField(db_column='AUID', max_length=20)  # Field name made lowercase.
    adatetime = models.CharField(db_column='Adatetime', max_length=50)  # Field name made lowercase.
    muid = models.CharField(db_column='MUID', max_length=20)  # Field name made lowercase.
    mdatetime = models.CharField(db_column='MDateTime', max_length=50)  # Field name made lowercase.
    supplyfrom = models.CharField(db_column='SupplyFrom', max_length=200)  # Field name made lowercase.
    destination = models.CharField(db_column='Destination', max_length=200)  # Field name made lowercase.
    forr = models.CharField(db_column='Forr', max_length=100)  # Field name made lowercase.
    annualqty = models.CharField(db_column='AnnualQty', max_length=50)  # Field name made lowercase.
    lotsize = models.CharField(db_column='LotSize', max_length=50)  # Field name made lowercase.
    approvedrate = models.CharField(db_column='ApprovedRate', max_length=50)  # Field name made lowercase.
    descriptionalias = models.CharField(db_column='DescriptionAlias', max_length=500)  # Field name made lowercase.
    job_lpi = models.CharField(db_column='Job_LPI', max_length=45)  # Field name made lowercase.
    blanket_no = models.CharField(db_column='Blanket_No', max_length=100)  # Field name made lowercase.
    wastagetemplateid = models.IntegerField(db_column='WastageTemplateID')  # Field name made lowercase.
    flap = models.CharField(db_column='Flap', max_length=10)  # Field name made lowercase.
    cartonweight = models.FloatField(db_column='CartonWeight')  # Field name made lowercase.
    estimaterecid = models.CharField(db_column='EstimateRecID', max_length=10)  # Field name made lowercase.
    collarflap = models.IntegerField(db_column='CollarFlap')  # Field name made lowercase.
    productcategory = models.IntegerField(db_column='ProductCategory')  # Field name made lowercase.
    excessvarince = models.CharField(db_column='Excessvarince', max_length=50)  # Field name made lowercase.
    opensize = models.CharField(db_column='OpenSize', max_length=100)  # Field name made lowercase.
    foldedsize = models.CharField(db_column='FoldedSize', max_length=100)  # Field name made lowercase.
    newrepeat = models.CharField(db_column='NewRepeat', max_length=20)  # Field name made lowercase.
    onlycorrugated = models.IntegerField(db_column='OnlyCorrugated')  # Field name made lowercase.
    jobtype = models.CharField(db_column='JobType', max_length=50)  # Field name made lowercase.
    sidepast = models.FloatField(db_column='SidePast')  # Field name made lowercase.
    otherdimension1 = models.FloatField(db_column='OtherDimension1')  # Field name made lowercase.
    otherdimension2 = models.FloatField(db_column='OtherDimension2')  # Field name made lowercase.
    otherdimension3 = models.FloatField(db_column='OtherDimension3')  # Field name made lowercase.
    flapsidegutter = models.FloatField(db_column='FlapSideGutter')  # Field name made lowercase.
    pastsidegutter = models.FloatField(db_column='PastSideGutter')  # Field name made lowercase.
    number_2dcode = models.IntegerField(db_column='2dcode')  # Field renamed because it wasn't a valid Python identifier.
    ref_itemid = models.CharField(db_column='Ref_ItemID', max_length=10)  # Field name made lowercase.
    isassembly = models.IntegerField(db_column='IsAssembly')  # Field name made lowercase.
    slength = models.FloatField(db_column='SLength')  # Field name made lowercase.
    sbreadth = models.FloatField(db_column='SBreadth')  # Field name made lowercase.
    sheight = models.FloatField(db_column='SHeight')  # Field name made lowercase.
    pershipperweight = models.FloatField(db_column='PerShipperWeight')  # Field name made lowercase.
    pershippercarton = models.FloatField(db_column='PerShipperCarton')  # Field name made lowercase.
    createddate = models.DateField(db_column='CreatedDate')  # Field name made lowercase.
    fulloutsource = models.IntegerField(db_column='FullOutSource')  # Field name made lowercase.
    marketing_approved = models.IntegerField(db_column='Marketing_Approved')  # Field name made lowercase.
    production_approved = models.IntegerField(db_column='Production_Approved')  # Field name made lowercase.
    qc_approved = models.IntegerField(db_column='QC_Approved')  # Field name made lowercase.
    bangladesh_job = models.IntegerField(db_column='BANGLADESH_JOB')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item_fpmasterext'


class ItemUnitMaster(models.Model):
    unitid = models.CharField(db_column='UnitID', primary_key=True, max_length=10)  # Field name made lowercase.
    unitname = models.CharField(db_column='UnitName', max_length=30, blank=True, null=True)  # Field name made lowercase.
    isactive = models.PositiveIntegerField(db_column='IsActive')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item_unit_master'


class ItemGroupMaster(models.Model):
    groupid = models.CharField(db_column='GroupID', max_length=10)  # Field name made lowercase.
    groupname = models.CharField(db_column='GroupName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    isactive = models.PositiveIntegerField(db_column='IsActive')  # Field name made lowercase.
    h = models.PositiveIntegerField(db_column='H')  # Field name made lowercase.
    gprefix = models.CharField(db_column='GPrefix', max_length=10)  # Field name made lowercase.
    current_no = models.CharField(db_column='Current_no', max_length=20)  # Field name made lowercase.
    gbasicdiscount = models.CharField(db_column='GBasicDiscount', max_length=10)  # Field name made lowercase.
    gexcise = models.CharField(db_column='GExcise', max_length=10)  # Field name made lowercase.
    garcess = models.CharField(db_column='GARCess', max_length=10)  # Field name made lowercase.
    geducess = models.CharField(db_column='GEduCess', max_length=10)  # Field name made lowercase.
    gshecess = models.CharField(db_column='GSheCess', max_length=10)  # Field name made lowercase.
    ginsurance = models.CharField(db_column='GInsurance', max_length=10)  # Field name made lowercase.
    gcommision = models.CharField(db_column='GCommision', max_length=10)  # Field name made lowercase.
    ginterest = models.CharField(db_column='GInterest', max_length=10)  # Field name made lowercase.
    gfreight = models.CharField(db_column='GFreight', max_length=10)  # Field name made lowercase.
    gpkg_fwd = models.CharField(db_column='GPkg_Fwd', max_length=10)  # Field name made lowercase.
    gvat = models.CharField(db_column='GVat', max_length=10)  # Field name made lowercase.
    gaddlvat = models.CharField(db_column='GAddlVat', max_length=10)  # Field name made lowercase.
    gtarrifadd = models.CharField(db_column='GTarrifAdd', max_length=10)  # Field name made lowercase.
    typesofgoods = models.CharField(db_column='TypesOfGoods', max_length=50)  # Field name made lowercase.
    lastitemcode = models.PositiveIntegerField(db_column='LastItemCode')  # Field name made lowercase.
    category = models.CharField(max_length=10)
    budgetper = models.FloatField()
    directpo = models.IntegerField(db_column='Directpo')  # Field name made lowercase.
    groupname_for_tally = models.CharField(db_column='GroupName_for_Tally', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item_group_master'


class Companymaster(models.Model):
    companyid = models.CharField(db_column='CompanyId', primary_key=True, max_length=10)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    shortname = models.CharField(db_column='ShortName', max_length=4, blank=True, null=True)  # Field name made lowercase.
    exciseper = models.FloatField(db_column='ExcisePer', blank=True, null=True)  # Field name made lowercase.
    localtaxper = models.FloatField(db_column='LocalTaxPer', blank=True, null=True)  # Field name made lowercase.
    carryingandforper = models.FloatField(db_column='CarryingAndForPer', blank=True, null=True)  # Field name made lowercase.
    packagingper = models.FloatField(db_column='PackagingPer', blank=True, null=True)  # Field name made lowercase.
    catid = models.CharField(db_column='CatID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    isactive = models.PositiveIntegerField(db_column='IsActive')  # Field name made lowercase.
    creditterm = models.CharField(db_column='CreditTerm', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cfminrate = models.FloatField(db_column='CFMinRate', blank=True, null=True)  # Field name made lowercase.
    cfminqty = models.FloatField(db_column='CFMinQty', blank=True, null=True)  # Field name made lowercase.
    cfkg = models.FloatField(db_column='CFKG', blank=True, null=True)  # Field name made lowercase.
    creditlimit = models.FloatField(db_column='CreditLimit', blank=True, null=True)  # Field name made lowercase.
    repid = models.CharField(db_column='RepID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    weburl = models.CharField(db_column='WebURL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(db_column='Remarks', blank=True, null=True)  # Field name made lowercase.
    isosvendor = models.PositiveIntegerField(db_column='IsOSVendor')  # Field name made lowercase.
    mantaininventory = models.PositiveIntegerField(db_column='MantainInventory')  # Field name made lowercase.
    packtemplate = models.CharField(db_column='PackTemplate', max_length=10)  # Field name made lowercase.
    commtemplate = models.CharField(db_column='CommTemplate', max_length=10)  # Field name made lowercase.
    eccno = models.CharField(db_column='ECCNo', max_length=45)  # Field name made lowercase.
    tin = models.CharField(db_column='TIN', max_length=45)  # Field name made lowercase.
    cstno = models.CharField(db_column='CSTNo', max_length=45)  # Field name made lowercase.
    payid = models.CharField(db_column='PayID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    auid = models.CharField(db_column='AUID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    adatetime = models.DateTimeField(db_column='ADateTime', blank=True, null=True)  # Field name made lowercase.
    muid = models.CharField(db_column='MUID', max_length=10)  # Field name made lowercase.
    mdatetime = models.CharField(db_column='MDateTime', max_length=50)  # Field name made lowercase.
    lstno = models.CharField(db_column='LSTNo', max_length=45)  # Field name made lowercase.
    shortname2 = models.CharField(db_column='ShortName2', max_length=60)  # Field name made lowercase.
    exciselicno = models.CharField(db_column='ExciseLicNo', max_length=45)  # Field name made lowercase.
    collectrate = models.CharField(db_column='Collectrate', max_length=45)  # Field name made lowercase.
    rangename = models.CharField(db_column='RangeName', max_length=45)  # Field name made lowercase.
    division = models.CharField(db_column='Division', max_length=45)  # Field name made lowercase.
    rangeadd = models.CharField(db_column='RangeAdd', max_length=250)  # Field name made lowercase.
    tanno = models.CharField(db_column='TANNo', max_length=45)  # Field name made lowercase.
    divadd = models.CharField(db_column='DivAdd', max_length=45)  # Field name made lowercase.
    clientstatus = models.CharField(db_column='ClientStatus', max_length=1)  # Field name made lowercase.
    clientgroup = models.CharField(db_column='ClientGroup', max_length=1)  # Field name made lowercase.
    ismother = models.IntegerField(db_column='Ismother')  # Field name made lowercase.
    motherid = models.CharField(db_column='Motherid', max_length=10)  # Field name made lowercase.
    lbtno = models.CharField(db_column='LBTNo', max_length=50)  # Field name made lowercase.
    segment = models.CharField(max_length=50, blank=True, null=True)
    delaytime = models.IntegerField(db_column='DelayTime')  # Field name made lowercase.
    cinno = models.CharField(db_column='CINNo', max_length=50)  # Field name made lowercase.
    plusmiusorderaccptance = models.FloatField(db_column='Plusmiusorderaccptance')  # Field name made lowercase.
    onhold = models.IntegerField(db_column='OnHold')  # Field name made lowercase.
    holdreason = models.CharField(db_column='HoldReason', max_length=100)  # Field name made lowercase.
    gstin = models.CharField(db_column='GSTIN', max_length=15)  # Field name made lowercase.
    labourprofitper = models.FloatField(db_column='LabourProfitPer')  # Field name made lowercase.
    type_dom_exp = models.CharField(db_column='Type_Dom_Exp', max_length=50)  # Field name made lowercase.
    transportationper = models.FloatField(db_column='Transportationper')  # Field name made lowercase.
    clientkey = models.CharField(db_column='Clientkey', max_length=8)  # Field name made lowercase.
    freightbyus = models.IntegerField(db_column='Freightbyus')  # Field name made lowercase.
    iswastage = models.IntegerField(db_column='IsWastage')  # Field name made lowercase.
    poselection = models.IntegerField(db_column='POSelection')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'companymaster'
        unique_together = (('companyid', 'ismother'),)


class ItemClass(models.Model):
    classid = models.CharField(db_column='classID', primary_key=True, max_length=10)  # Field name made lowercase.
    classname = models.CharField(db_column='className', max_length=500)  # Field name made lowercase.
    isactive = models.PositiveIntegerField(db_column='IsActive')  # Field name made lowercase.
    cexcise = models.CharField(db_column='CExcise', max_length=10)  # Field name made lowercase.
    cedcess = models.CharField(db_column='CEDCess', max_length=10)  # Field name made lowercase.
    cshecess = models.CharField(db_column='CSHECess', max_length=10)  # Field name made lowercase.
    cvat = models.CharField(db_column='CVAT', max_length=10)  # Field name made lowercase.
    ctarrifadd = models.CharField(db_column='CTarrifAdd', max_length=10)  # Field name made lowercase.
    excisedetailid = models.IntegerField(db_column='ExciseDetailId')  # Field name made lowercase.
    igst = models.DecimalField(db_column='IGST', max_digits=5, decimal_places=2)  # Field name made lowercase.
    cgst = models.DecimalField(db_column='CGST', max_digits=5, decimal_places=2)  # Field name made lowercase.
    sgst = models.DecimalField(db_column='SGST', max_digits=5, decimal_places=2)  # Field name made lowercase.
    lclassid = models.CharField(db_column='LClassid', max_length=10)  # Field name made lowercase.
    iclassid = models.CharField(db_column='IClassid', max_length=10)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'item_class'
