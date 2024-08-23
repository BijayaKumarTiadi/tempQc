from django.db import models

class TextMatterChecking(models.Model):
    autoid = models.AutoField(db_column='AutoId', primary_key=True)
    docid = models.CharField(db_column='DocID', unique=True, max_length=20)
    criticaldefect = models.CharField(db_column='CriticalDefect', max_length=50)
    checkdate = models.DateTimeField(db_column='CheckDate')
    partialcheckdate = models.DateTimeField(db_column='PartialCheckDate')
    fullcheckdate = models.DateTimeField(db_column='FullCheckDate')
    checkingmethod = models.CharField(db_column='CheckingMethod', max_length=50)
    checkedby = models.CharField(db_column='CheckedBy', max_length=10)
    remarks = models.CharField(db_column='Remarks', max_length=200)
    adatetime = models.DateTimeField(db_column='AdateTime', blank=True, null=True)
    mdatetime = models.DateTimeField(db_column='MdateTime', blank=True, null=True)
    

    class Meta:
        managed = False
        db_table = 'text_matter_checking'


class Colorcheckingreport(models.Model):
    autoid = models.AutoField(db_column='AutoId', primary_key=True)
    jobid = models.CharField(db_column='JobId', max_length=25)
    ink = models.CharField(db_column='Ink', max_length=50)
    jobname = models.CharField(db_column='JobName', max_length=250)
    delta = models.CharField(db_column='Delta', max_length=100)
    manualaproval = models.CharField(db_column='ManualAproval', max_length=100)
    remarks = models.CharField(db_column='Remarks', max_length=100, blank=True, null=True)
    adatetime = models.DateTimeField(db_column='AdateTime')
    mdatetime = models.DateTimeField(db_column='MdateTime')

    class Meta:
        managed = False
        db_table = 'ColorCheckingReport'
