# Generated by Django 5.2.2 on 2025-06-08 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(default=1, verbose_name='Review'),
            preserve_default=False,
        ),
    ]
