# Generated by Django 2.1.8 on 2021-08-31 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_extract', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tls_feature',
            name='name',
            field=models.CharField(default='0', max_length=10),
        ),
    ]