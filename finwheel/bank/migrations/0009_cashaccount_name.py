# Generated by Django 4.2.3 on 2024-10-05 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0008_externalbankaccount_ach_authorized_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashaccount',
            name='name',
            field=models.TextField(null=True),
        ),
    ]
