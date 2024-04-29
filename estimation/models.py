from django.utils import timezone
from django.db import models
from imagekit.models import ProcessedImageField

#for signal savings
from django.dispatch import receiver

from django.db.models.signals import pre_save
from accounts.models import ChangeLog
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType

class EstItemtypemaster(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    CartonType = models.CharField(db_column='CartonType', max_length=60)  
    carton_cat = models.CharField(db_column='carton_cat', max_length=20)  
    internalCartonType = models.CharField(db_column='internalCartonType', unique=True, max_length=60)  
    # imgpath = models.CharField(db_column='ImgPath', max_length=200, blank=True, null=True)  
    imgpath = ProcessedImageField(upload_to='estimation/itemtypemaster/',format='JPEG',options={'quality': 40}, null=True)#if you want to use icons for the specific module
    ecma_code = models.CharField(db_column='ECMA_Code', max_length=50, blank=True, null=True)  
    hover_imgpath = ProcessedImageField(upload_to='estimation/itemtypemaster_hover/',format='JPEG',options={'quality': 40}, null=True)
    class Meta:
        managed = False
        db_table = 'est_itemtypemaster'
        unique_together = (('id', 'CartonType'),)
    def __str__(self):
        return self.CartonType

class EstAdvanceInputDetail(models.Model):
    #this is for the advsance input detailss
    id = models.AutoField(db_column='ID', primary_key=True)
    unique_name = models.CharField(db_column='Unique_Name', max_length=20)
    input_label_name = models.CharField(max_length=30)
    input_type = models.CharField(max_length=30, blank=True, null=True)
    input_data_type = models.CharField(max_length=30, blank=True, null=True)
    input_default_value = models.CharField(max_length=10, blank=True, null=True)
    seqno = models.IntegerField(db_column='SeqNo', blank=True, null=True)
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True) 

    class Meta:
        managed = False
        db_table = 'est_advance_input_detail'



class EstItemtypedetail(models.Model):
    master = models.ForeignKey(EstItemtypemaster, models.DO_NOTHING, db_column='Master_ID', blank=True, null=True, related_name='itemtypedetail_set')  
    int_id = models.AutoField(db_column='Int_ID', primary_key=True)  
    label_name = models.CharField(db_column='Label_Name', max_length=50)  
    default_value = models.FloatField(db_column='Default_Value')  
    min_value = models.FloatField(db_column='Min_Value', blank=True, null=True)  
    max_value = models.FloatField(db_column='Max_Value', blank=True, null=True)  
    tooltip = models.CharField(db_column='ToolTip', max_length=100)  
    seqid = models.IntegerField(db_column='SeqID', blank=True, null=True)  
    remark = models.CharField(db_column='Remark', max_length=100, blank=True, null=True)  
    isactive = models.IntegerField(db_column='IsActive')  
    isrequired = models.IntegerField(db_column='IsRequired')  
    cellheight = models.FloatField(db_column='CellHeight', blank=True, null=True)  
    cellwidth = models.FloatField(db_column='CellWidth', blank=True, null=True)  
    imgpath = ProcessedImageField(upload_to='estimation/itemtypedetails/',format='JPEG',options={'quality': 40}, null=True)#if you want to use icons for the specific module
    
    #ALTER TABLE est_itemtypedetail ADD COLUMN ImgPath VARCHAR(200); this is added manually.

    class Meta:
        managed = False
        db_table = 'est_itemtypedetail'
        unique_together = (('int_id', 'label_name'), ('master', 'label_name'),)
    def __str__(self):
        return self.label_name




class Papermasterfull(models.Model):
    paperid = models.CharField(db_column='PaperId', primary_key=True, max_length=10)  
    paperkind = models.CharField(db_column='PaperKind', max_length=50, blank=True, null=True)  
    manucompany = models.CharField(db_column='ManuCompany', max_length=50, blank=True, null=True)  
    gsm = models.IntegerField(db_column='Gsm', blank=True, null=True)  
    grain = models.CharField(db_column='Grain', max_length=10, blank=True, null=True)  
    costprice = models.FloatField(db_column='CostPrice', blank=True, null=True)  
    unit = models.CharField(db_column='Unit', max_length=10, blank=True, null=True)  
    standardlength = models.FloatField(db_column='StandardLength', blank=True, null=True)  
    standardbreadth = models.FloatField(db_column='StandardBreadth', blank=True, null=True)  
    pquantity = models.FloatField(db_column='PQuantity', blank=True, null=True)  
    stock = models.CharField(db_column='Stock', max_length=20)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10, blank=True, null=True)  
    shperpacket = models.SmallIntegerField(db_column='ShPerPacket', blank=True, null=True)  
    packetweight = models.FloatField(db_column='PacketWeight', blank=True, null=True)  
    remark = models.CharField(db_column='Remark', max_length=50, blank=True, null=True)  
    isspecial = models.PositiveIntegerField(db_column='IsSpecial')  
    pkind = models.CharField(db_column='PKind', max_length=45)  
    fsctype = models.IntegerField(db_column='FSCType')  
    isactive = models.IntegerField(db_column='IsActive')  
    paperbrand = models.CharField(db_column='PaperBrand', max_length=30)  
    classid = models.CharField(db_column='Classid', max_length=10)  
    bf = models.IntegerField(db_column='BF')  
    thickness = models.FloatField(db_column='Thickness')  
    uom = models.CharField(db_column='UOM', max_length=10)  
    subgroupid = models.IntegerField(db_column='SubGroupID')  

    class Meta:
        managed = False
        db_table = 'papermasterfull'



class EstProcessInputDetail(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    prid = models.CharField(db_column='PrID', max_length=50)  
    sp_process_no = models.IntegerField(db_column='SP_Process_no')  
    input_label_name = models.CharField(max_length=30)
    input_type = models.CharField(max_length=30, blank=True, null=True)
    input_data_type = models.CharField(max_length=30, blank=True, null=True)
    input_default_value = models.CharField(max_length=10, blank=True, null=True)
    Unique_Name = models.CharField(max_length=20, blank=True, null=True)
    seqno = models.IntegerField(db_column='SeqNo', blank=True, null=True)  
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'est_process_input_detail'


class FrontendResponse(models.Model):
    json_response = models.JSONField()
    created_by = models.CharField(max_length=150)  # Assuming 150 characters is sufficient for the login name
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=150)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Response ID: {self.pk}"
    

# Below tables are for the input from the process input page , total 9 tables 

class EstNewQuote(models.Model):
    quoteid = models.AutoField(db_column='QuoteID', primary_key=True)  
    quotedate = models.CharField(db_column='QuoteDate', max_length=10)  
    quote_no = models.CharField(db_column='Quote_No', max_length=30)  
    icompanyid = models.CharField(db_column='ICompanyID', max_length=10)  
    clientid = models.CharField(db_column='ClientID', max_length=10, blank=True, null=True)  
    client_name = models.CharField(db_column='Client_Name', max_length=100, blank=True, null=True)  
    product_name = models.CharField(db_column='Product_Name', max_length=100, blank=True, null=True)  
    product_code = models.CharField(db_column='Product_Code', max_length=20, blank=True, null=True)  
    carton_type_id = models.IntegerField(db_column='Carton_Type_ID', blank=True, null=True)  
    auid = models.CharField(db_column='AUID', max_length=10)
    adatetime = models.DateTimeField(db_column='ADateTime', auto_now_add=True)  
    muid = models.CharField(db_column='MUID', max_length=10, blank=True, null=True)
    mdatetime = models.DateTimeField(db_column='MDateTime', blank=True, null=True)  
    remarks = models.CharField(db_column='Remarks', max_length=200, blank=True, null=True)  
    orderstatus = models.CharField(db_column='OrderStatus', max_length=20, blank=True, null=True)  
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)  
    finalby = models.CharField(db_column='FinalBy', max_length=10, blank=True, null=True)  
    enqno = models.CharField(db_column='EnqNo', max_length=10, blank=True, null=True)  
    docnotion = models.IntegerField(db_column='DocNotion', blank=True, null=True)  
    estnotion = models.CharField(db_column='EstNotion', max_length=50, blank=True, null=True)  
    finaldate = models.DateTimeField(db_column='FinalDate', blank=True, null=True)  
    repid = models.CharField(db_column='RepID', max_length=10, blank=True, null=True)  
    impexpstatus = models.CharField(db_column='ImpExpStatus', max_length=2, blank=True, null=True)  
    revquoteno = models.IntegerField(db_column='RevQuoteNo', blank=True, null=True)  
    grainstyle = models.IntegerField(db_column='GrainStyle', blank=True, null=True)  
    locationid = models.CharField(db_column='LocationID', max_length=10, blank=True, null=True)  
    currencyid = models.CharField(db_column='CurrencyID', max_length=10, blank=True, null=True)  
    currency_factctor = models.FloatField(db_column='Currency_Factctor', blank=True, null=True)  
    currency_curramt = models.FloatField(db_column='Currency_CurrAmt', blank=True, null=True)  
    clientcategoryid = models.CharField(db_column='ClientCategoryID', max_length=10, blank=True, null=True)  
    calculatedrate = models.FloatField(db_column='CalculatedRate', blank=True, null=True)  
    quoterate = models.FloatField(db_column='QuoteRate', blank=True, null=True)  
    finalrate = models.FloatField(db_column='FinalRate', blank=True, null=True)  
    fpid = models.CharField(db_column='FPID', max_length=10, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'Est_New_quote'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        is_new = not self.pk  # HEre Check if the instance has a primary key 
        super().save(*args, **kwargs)
        action_flag = ADDITION if is_new else CHANGE
        if request:
            try:
                ChangeLog.objects.create(
                    object_id=str(self.quoteid),
                    object_repr=str(self),
                    action_flag=action_flag,
                    change_message='',
                    content_type=ContentType.objects.get_for_model(self.__class__),
                    user=request.user,
                )
            except Exception as e:
                print(f"Error logging change: {e}")

    def delete(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if request is None and 'context' in kwargs:
            request = kwargs['context'].get('request')
        object_id = str(self.quoteid) if self.quoteid else None
        object_repr = f"{self.__class__.__name__} object ({object_id})" if object_id else f"{self.__class__.__name__} object (None)"
        super().delete(*args, **kwargs)
        try:
            ChangeLog.objects.create(
                object_id=object_id,
                object_repr=object_repr,
                action_flag=DELETION,
                change_message='',
                content_type=ContentType.objects.get_for_model(self.__class__),
                user=request.user if request else None,
            )
        except Exception as e:
            print(f"Error logging deletion: {e}")

@receiver(pre_save, sender=EstNewQuote)
def update_estnewquote_log(sender, instance, **kwargs):
    request = getattr(instance, 'request', None)
    
    if not instance.auid:
        # If auid is not set, it means the record is being created
        if request:
            instance.auid = str(request.user.id)
        instance.adatetime = timezone.now()
    else:
        # If auid is set, it means the record is being updated
        if request:
            instance.muid = str(request.user.id)
        instance.mdatetime = timezone.now()



class EstQty(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    qtyreq = models.IntegerField(db_column='QtyReq', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'Est_Qty'


class EstBoard(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    boardid = models.CharField(db_column='BoardID', max_length=10, blank=True, null=True)  
    board_type = models.CharField(db_column='Board_Type', max_length=10, blank=True, null=True)  
    board_gsm = models.CharField(db_column='Board_GSM', max_length=10, blank=True, null=True)  
    board_menufac = models.CharField(db_column='board_menufac', max_length=50, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'Est_Board'


class EstMetpetp(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    mp_ft = models.CharField(db_column='MP_FT', max_length=10, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'est_metpetp'


class EstPrint(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    pr_complex = models.CharField(db_column='Pr_Complex', max_length=10, blank=True, null=True)  
    pr_fcol = models.IntegerField(db_column='Pr_FCol')  
    pr_fb = models.CharField(db_column='Pr_FB', max_length=10)  
    pr_add_pl = models.IntegerField(db_column='Pr_Add_Pl')  

    class Meta:
        managed = False
        db_table = 'Est_Print'


class EstCoating(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    fc_type = models.CharField(db_column='FC_Type', max_length=10, blank=True, null=True)  
    fc_kind = models.CharField(db_column='FC_Kind', max_length=10)  
    fc_area = models.FloatField(db_column='FC_Area')  
    fc_fb = models.CharField(db_column='FB', max_length=10)  

    class Meta:
        managed = False
        db_table = 'Est_coating'


class EstLamination(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    fl_film = models.CharField(db_column='FL_Film', max_length=10, blank=True, null=True)  
    fl_type = models.CharField(db_column='FL_Type', max_length=10)  
    fl_strips = models.IntegerField(db_column='FL_Strips')  
    fl_fb = models.CharField(db_column='FB', max_length=10)  

    class Meta:
        managed = False
        db_table = 'Est_lamination'


class EstFoiling(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    ff_film = models.CharField(db_column='FF_Film', max_length=10, blank=True, null=True)  
    ff_l = models.FloatField(db_column='FF_L')  
    ff_b = models.FloatField(db_column='FF_B')  
    ff_fb = models.CharField(db_column='FB', max_length=10)  

    class Meta:
        managed = False
        db_table = 'Est_Foiling'


class EstGrainDirection(models.Model):
    grain_direction = models.CharField(max_length=1)
    quoteid = models.IntegerField(db_column='QuoteID')  

    class Meta:
        managed = False
        db_table = 'est_grain_direction'

class EstDimensions(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    quoteid = models.IntegerField(db_column='QuoteID')
    dimension_id = models.CharField(db_column='Dimension_ID',max_length=10)
    dimension_value = models.FloatField(db_column='Dimension_value')

    class Meta:
        managed = False
        db_table = 'Est_Dimensions'

class EstPunching(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    pn_type = models.CharField(db_column='PN_Type', max_length=10, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'est_punching'


class EstEmbossing(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    em_type = models.CharField(db_column='EM_Type', max_length=10, blank=True, null=True)  
    em_block_l = models.FloatField(db_column='EM_BLOCK_L')  
    em_block_b = models.FloatField(db_column='EM_BLOCK_B')  
    fb = models.CharField(db_column='FB', max_length=10)  

    class Meta:
        managed = False
        db_table = 'est_embossing'


class EstPasting(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    pa_type = models.CharField(db_column='Pa_Type', max_length=10, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'est_pasting'


class EstWindowPatching(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    wp_film = models.CharField(db_column='WP_Film', max_length=10, blank=True, null=True)  
    wp_l = models.FloatField(db_column='WP_L')  
    wp_b = models.FloatField(db_column='WP_B')  

    class Meta:
        managed = False
        db_table = 'est_window_patching'


class EstLinerBag(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    type_113 = models.CharField(db_column='Type_113', max_length=10, blank=True, null=True)
    l_113 = models.FloatField(db_column='L_113')
    b_113 = models.FloatField(db_column='B_113')

    class Meta:
        managed = False
        db_table = 'est_liner_bag'


class EstCorrugation(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    fm_tot_ply = models.IntegerField(db_column='FM_Tot_Ply', blank=True, null=True)  
    fm_flute = models.CharField(db_column='FM_Flute', max_length=10)  
    fm_kraft_det = models.CharField(db_column='FM_KRAFT_Det', max_length=10)  
    fm_pins = models.CharField(db_column='FM_Pins', max_length=2)  

    class Meta:
        managed = False
        db_table = 'est_corrugation'


class EstOtherProcess(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    op_process = models.CharField(db_column='OP_Process', max_length=10, blank=True, null=True)  
    op_qty = models.FloatField(db_column='OP_Qty')  
    op_rem = models.CharField(db_column='OP_Rem', max_length=100)  

    class Meta:
        managed = False
        db_table = 'est_Other_process'


class EstOtp(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    op_process_id = models.CharField(db_column='OP_Process_ID', max_length=10, blank=True, null=True)  
    op_rate = models.FloatField(db_column='OP_Rate')  
    op_rem = models.CharField(db_column='OP_Rem', max_length=100)  

    class Meta:
        managed = False
        db_table = 'est_OTP'


class EstFolding(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    fo_cross_fold = models.IntegerField(db_column='FO_Cross_Fold', blank=True, null=True)  
    fo_verticle_fold = models.IntegerField(db_column='FO_Verticle_Fold')  
    fo_gum_tape = models.CharField(db_column='FO_GUM_Tape', max_length=10)  

    class Meta:
        managed = False
        db_table = 'est_folding'


class EstBbp(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    bbp_board = models.CharField(db_column='BBP_Board', max_length=10, blank=True, null=True)  
    bbp_gsm = models.IntegerField(db_column='BBP_GSM')  

    class Meta:
        managed = False
        db_table = 'est_BBP'


class EstSorting(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  
    quoteid = models.IntegerField(db_column='QuoteID')  
    so_style = models.CharField(db_column='SO_Style', max_length=10, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'est_sorting'

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

class Currencymaster(models.Model):
    currencyid = models.CharField(db_column='CurrencyID', primary_key=True, max_length=10) 
    currencyname = models.CharField(db_column='CurrencyName', max_length=50, blank=True, null=True) 
    currencysymbol = models.CharField(db_column='CurrencySymbol', max_length=20, db_collation='utf8_general_ci', blank=True, null=True) 
    isdefault = models.PositiveIntegerField(db_column='IsDefault') 
    hexacode = models.CharField(db_column='HexaCode', max_length=6) 

    class Meta:
        managed = False
        db_table = 'currencymaster'

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


class PapergridQtyP(models.Model):
    """
    This table used to fetch the detailed data from the PapergridQty which inside procedure we converted it to the permanet table .
    """
    inc = models.FloatField(db_column='Inc')  
    dackle_dim = models.FloatField(db_column='Dackle_Dim')  
    grain_dim = models.FloatField(db_column='Grain_Dim')  
    ups = models.IntegerField(db_column='Ups')  
    areapercarton_sqinch = models.FloatField(db_column='AreaPerCarton_SqInch')  
    scan = models.IntegerField(db_column='Scan')  
    grain = models.CharField(db_column='Grain', max_length=10)  
    machineid = models.CharField(db_column='MachineID', max_length=10)  
    machinename = models.CharField(db_column='MachineName', max_length=60)  
    noofpass_req = models.IntegerField(db_column='NoOfPass_req')  
    mat_x = models.IntegerField(db_column='Mat_X')  
    mat_y = models.IntegerField(db_column='Mat_Y')  
    dielength_in_inch = models.FloatField(db_column='DieLength_In_Inch', blank=True, null=True)  
    qty = models.FloatField(db_column='Qty')  
    f_color = models.IntegerField(db_column='F_Color')  
    b_color = models.IntegerField(db_column='B_Color')  
    die_planheight = models.FloatField(db_column='Die_PlanHeight')  
    die_planwidth = models.FloatField(db_column='Die_PlanWidth')  
    fullsheet_d = models.FloatField(db_column='FullSheet_D')  
    fullsheet_g = models.FloatField(db_column='FullSheet_G')  
    fullsheet_grain = models.CharField(db_column='FullSheet_Grain', max_length=10)  
    fullsheet_cut_x = models.IntegerField(db_column='FullSheet_Cut_X')  
    fullsheet_cut_y = models.IntegerField(db_column='FullSheet_Cut_Y')  
    fullsheet_ups = models.IntegerField(db_column='FullSheet_Ups')  
    sheets_a = models.FloatField(db_column='Sheets_A')  
    heightcut = models.IntegerField(db_column='HeightCut')  
    widthcut = models.IntegerField(db_column='WidthCut')  
    lengthremaining = models.FloatField(db_column='LengthRemaining')  
    widthremaining = models.FloatField(db_column='WidthRemaining')  
    itemsinfirstcut = models.IntegerField(db_column='ItemsInFirstCut')  
    totalcuts = models.IntegerField(db_column='TotalCuts')  
    totalbox = models.IntegerField(db_column='TotalBox')  
    dackle_dim_b = models.FloatField(db_column='Dackle_Dim_B')  
    grain_dim_b = models.FloatField(db_column='Grain_Dim_B')  
    ups_b = models.IntegerField(db_column='Ups_B')  
    mat_x_b = models.IntegerField(db_column='Mat_X_B')  
    mat_y_b = models.IntegerField(db_column='Mat_Y_B')  
    cuts_b = models.IntegerField(db_column='Cuts_B')  
    sheets_b = models.FloatField(db_column='Sheets_B')  
    dackle_dim_c = models.FloatField(db_column='Dackle_Dim_C')  
    grain_dim_c = models.FloatField(db_column='Grain_Dim_C')  
    ups_c = models.IntegerField(db_column='Ups_C')  
    mat_x_c = models.IntegerField(db_column='Mat_X_C')  
    mat_y_c = models.IntegerField(db_column='Mat_Y_C')  
    cuts_c = models.IntegerField(db_column='Cuts_C')  
    sheets_c = models.FloatField(db_column='Sheets_C')  
    dackle_dim_d = models.FloatField(db_column='Dackle_Dim_D')  
    grain_dim_d = models.FloatField(db_column='Grain_Dim_D')  
    ups_d = models.IntegerField(db_column='Ups_D')  
    mat_x_d = models.IntegerField(db_column='Mat_X_D')  
    mat_y_d = models.IntegerField(db_column='Mat_Y_D')  
    cuts_d = models.IntegerField(db_column='Cuts_D')  
    sheets_d = models.FloatField(db_column='Sheets_D')  
    dackle_dim_tot = models.FloatField(db_column='Dackle_Dim_Tot')  
    grain_dim_tot = models.FloatField(db_column='Grain_Dim_Tot')  
    wastage_x = models.FloatField(db_column='Wastage_X')  
    wastage_y = models.FloatField(db_column='Wastage_Y')  
    wastage_weight_kg_a = models.FloatField(db_column='Wastage_Weight_kg_A')  
    wastage_weight_kg_b = models.FloatField(db_column='Wastage_Weight_kg_B')  
    wastage_weight_kg = models.FloatField(db_column='Wastage_Weight_kg')  
    utilizationper = models.FloatField(db_column='UtilizationPer')  
    fullsheet_req = models.FloatField(db_column='FullSheet_Req')  
    paperid = models.CharField(db_column='PaperID', max_length=10)  
    gsm = models.IntegerField(db_column='Gsm')  
    paper_rate = models.FloatField(db_column='Paper_Rate')  
    paper_unit = models.CharField(db_column='Paper_Unit', max_length=10)  
    print_size_sheets = models.FloatField(db_column='Print_Size_Sheets')  
    print_impression = models.IntegerField(db_column='Print_Impression')  
    paper_kg = models.FloatField(db_column='Paper_Kg')  
    paper_kg_fullsheet = models.FloatField(db_column='Paper_Kg_FullSheet')  
    paper_amt = models.FloatField(db_column='Paper_Amt')  
    punchdie_amt = models.FloatField(db_column='PunchDie_Amt')  
    plate_amt = models.FloatField(db_column='Plate_Amt')  
    prmake_ready_amt = models.FloatField(db_column='PrMake_Ready_Amt')  
    printing_amt = models.FloatField(db_column='Printing_Amt')  
    total_amt = models.FloatField(db_column='Total_Amt')  
    pn_mcid = models.CharField(db_column='PN_McID', max_length=10)  
    pn_machinename = models.CharField(db_column='PN_MachineName', max_length=60)  
    pn_maxdackle = models.IntegerField(db_column='PN_MaxDackle')  
    pn_mindackle = models.IntegerField(db_column='PN_MinDackle')  
    pn_maxgrain = models.IntegerField(db_column='PN_MaxGrain')  
    pn_mingrain = models.IntegerField(db_column='PN_MinGrain')  
    pn_gripper = models.IntegerField(db_column='PN_Gripper')  
    pn_makerdy_amt = models.FloatField(db_column='PN_MakeRdy_Amt', blank=True, null=True)  
    pn_punching_amt = models.FloatField(db_column='PN_Punching_Amt', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'PaperGrid_Qty_P'
        auto_created = False