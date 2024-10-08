# Generated by Django 3.2.19 on 2024-08-21 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mastersapp', '0004_itemdimension_itemmaster_textmatterchecking'),
    ]

    operations = [
        migrations.CreateModel(
            name='Colorcheckingreport',
            fields=[
                ('autoid', models.AutoField(db_column='AutoId', primary_key=True, serialize=False)),
                ('jobid', models.CharField(db_column='JobId', max_length=25)),
                ('ink', models.CharField(db_column='Ink', max_length=50)),
                ('jobname', models.CharField(db_column='JobName', max_length=250)),
                ('delta', models.CharField(db_column='Delta', max_length=100)),
                ('manualaproval', models.CharField(db_column='ManualAproval', max_length=100)),
                ('remarks', models.CharField(blank=True, db_column='Remarks', max_length=100, null=True)),
                ('adatetime', models.DateTimeField(db_column='AdateTime')),
                ('mdatetime', models.DateTimeField(db_column='MdateTime')),
            ],
            options={
                'db_table': 'ColorCheckingReport',
                'managed': False,
            },
        ),
    ]
