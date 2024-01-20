# Generated by Django 2.2.28 on 2023-03-30 19:14

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import email.utils
import ietf.message.models
import ietf.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0001_initial'),
        ('person', '0001_initial'),
        ('name', '0001_initial'),
        ('doc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('subject', ietf.message.models.HeaderField()),
                ('frm', ietf.message.models.HeaderField()),
                ('to', ietf.message.models.HeaderField()),
                ('cc', ietf.message.models.HeaderField(blank=True)),
                ('bcc', ietf.message.models.HeaderField(blank=True)),
                ('reply_to', ietf.message.models.HeaderField(blank=True)),
                ('body', models.TextField()),
                ('content_type', models.CharField(blank=True, default='text/plain', max_length=255)),
                ('msgid', ietf.message.models.HeaderField(blank=True, default=email.utils.make_msgid, null=True)),
                ('sent', models.DateTimeField(blank=True, null=True)),
                ('by', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
                ('related_docs', models.ManyToManyField(blank=True, to='doc.Document')),
                ('related_groups', models.ManyToManyField(blank=True, to='group.Group')),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='SendQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('send_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('note', models.TextField(blank=True)),
                ('by', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
                ('message', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Message')),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='MessageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, db_index=True, max_length=255)),
                ('content_type', models.CharField(blank=True, max_length=255)),
                ('encoding', models.CharField(blank=True, max_length=255)),
                ('removed', models.BooleanField(default=False)),
                ('body', models.TextField()),
                ('message', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Message')),
            ],
        ),
        migrations.CreateModel(
            name='AnnouncementFrom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('group', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
                ('name', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.RoleName')),
            ],
            options={
                'verbose_name_plural': 'Announcement From addresses',
            },
        ),
        migrations.AddIndex(
            model_name='sendqueue',
            index=models.Index(fields=['time'], name='message_sen_time_07ab31_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['time'], name='message_mes_time_20eabf_idx'),
        ),
    ]