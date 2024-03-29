# Generated by Django 4.0.10 on 2023-05-16 20:36

from django.db import migrations
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0001_initial'),
        ('doc', '0003_remove_document_info_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dochistory',
            name='ad',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ad_%(class)s_set', to='person.person', verbose_name='area director'),
        ),
        migrations.AlterField(
            model_name='dochistory',
            name='shepherd',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shepherd_%(class)s_set', to='person.email'),
        ),
        migrations.AlterField(
            model_name='document',
            name='ad',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ad_%(class)s_set', to='person.person', verbose_name='area director'),
        ),
        migrations.AlterField(
            model_name='document',
            name='shepherd',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shepherd_%(class)s_set', to='person.email'),
        ),
    ]
