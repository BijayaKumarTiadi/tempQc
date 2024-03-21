from django.db import models
from imagekit.models import ProcessedImageField

class EstItemtypemaster(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    CartonType = models.CharField(db_column='CartonType', max_length=60)  # Field name made lowercase.
    internalCartonType = models.CharField(db_column='internalCartonType', unique=True, max_length=60)  # Field name made lowercase.
    # imgpath = models.CharField(db_column='ImgPath', max_length=200, blank=True, null=True)  # Field name made lowercase.
    imgpath = ProcessedImageField(upload_to='estimation/itemtypemaster/',format='JPEG',options={'quality': 40}, null=True)#if you want to use icons for the specific module
    ecma_code = models.CharField(db_column='ECMA_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hover_imgpath = ProcessedImageField(upload_to='estimation/itemtypemaster_hover/',format='JPEG',options={'quality': 40}, null=True)
    class Meta:
        managed = False
        db_table = 'est_itemtypemaster'
        unique_together = (('id', 'CartonType'),)
    def __str__(self):
        return self.CartonType



class EstItemtypedetail(models.Model):
    master = models.ForeignKey(EstItemtypemaster, models.DO_NOTHING, db_column='Master_ID', blank=True, null=True, related_name='itemtypedetail_set')  # Field name made lowercase.
    int_id = models.AutoField(db_column='Int_ID', primary_key=True)  # Field name made lowercase.
    label_name = models.CharField(db_column='Label_Name', max_length=50)  # Field name made lowercase.
    default_value = models.FloatField(db_column='Default_Value')  # Field name made lowercase.
    min_value = models.FloatField(db_column='Min_Value', blank=True, null=True)  # Field name made lowercase.
    max_value = models.FloatField(db_column='Max_Value', blank=True, null=True)  # Field name made lowercase.
    tooltip = models.CharField(db_column='ToolTip', max_length=100)  # Field name made lowercase.
    seqid = models.IntegerField(db_column='SeqID', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive')  # Field name made lowercase.
    isrequired = models.IntegerField(db_column='IsRequired')  # Field name made lowercase.
    cellheight = models.FloatField(db_column='CellHeight', blank=True, null=True)  # Field name made lowercase.
    cellwidth = models.FloatField(db_column='CellWidth', blank=True, null=True)  # Field name made lowercase.
    imgpath = ProcessedImageField(upload_to='estimation/itemtypedetails/',format='JPEG',options={'quality': 40}, null=True)#if you want to use icons for the specific module
    
    #ALTER TABLE est_itemtypedetail ADD COLUMN ImgPath VARCHAR(200); this is added manually.

    class Meta:
        managed = False
        db_table = 'est_itemtypedetail'
        unique_together = (('int_id', 'label_name'), ('master', 'label_name'),)
    def __str__(self):
        return self.label_name
