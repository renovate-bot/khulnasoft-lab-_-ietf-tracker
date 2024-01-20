# Generated by Django 2.2.28 on 2023-03-20 19:22

from django.conf import settings
import django.contrib.postgres.fields.citext
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import ietf.person.models
import ietf.utils.models
import ietf.utils.storage
import jsonfield.fields
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('name', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(db_index=True, help_text='Preferred long form of name.', max_length=255, validators=[ietf.person.models.name_character_validator], verbose_name='Full Name (Unicode)')),
                ('plain', models.CharField(blank=True, default='', help_text="Use this if you have a Spanish double surname.  Don't use this for nicknames, and don't use it unless you've actually observed that the datatracker shows your name incorrectly.", max_length=64, verbose_name='Plain Name correction (Unicode)')),
                ('ascii', models.CharField(help_text='Name as rendered in ASCII (Latin, unaccented) characters.', max_length=255, verbose_name='Full Name (ASCII)')),
                ('ascii_short', models.CharField(blank=True, help_text='Example: A. Nonymous.  Fill in this with initials and surname only if taking the initials and surname of the ASCII name above produces an incorrect initials-only form. (Blank is OK).', max_length=32, null=True, verbose_name='Abbreviated Name (ASCII)')),
                ('pronouns_selectable', jsonfield.fields.JSONCharField(blank=True, default=list, max_length=120, null=True, verbose_name='Pronouns')),
                ('pronouns_freetext', models.CharField(blank=True, help_text='Optionally provide your personal pronouns. These will be displayed on your public profile page and alongside your name in Meetecho and, in future, other systems. Select any number of the checkboxes OR provide a custom string up to 30 characters.', max_length=30, null=True, verbose_name=' ')),
                ('biography', models.TextField(blank=True, help_text='Short biography for use on leadership pages. Use plain text or reStructuredText markup.')),
                ('photo', models.ImageField(blank=True, default=None, storage=ietf.utils.storage.NoLocationMigrationFileSystemStorage(location=None), upload_to='photo')),
                ('photo_thumb', models.ImageField(blank=True, default=None, storage=ietf.utils.storage.NoLocationMigrationFileSystemStorage(location=None), upload_to='photo')),
                ('name_from_draft', models.CharField(editable=False, help_text='Name as found in an Internet-Draft submission.', max_length=255, null=True, verbose_name='Full Name (from submission)')),
                ('user', ietf.utils.models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PersonEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now, help_text='When the event happened')),
                ('type', models.CharField(choices=[('apikey_login', 'API key login'), ('email_address_deactivated', 'Email address deactivated')], max_length=50)),
                ('desc', models.TextField()),
                ('person', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
            ],
            options={
                'ordering': ['-time', '-id'],
            },
        ),
        migrations.CreateModel(
            name='PersonApiKeyEvent',
            fields=[
                ('personevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='person.PersonEvent')),
            ],
            bases=('person.personevent',),
        ),
        migrations.CreateModel(
            name='PersonExtResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, default='', max_length=255)),
                ('value', models.CharField(max_length=2083)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.ExtResourceName')),
                ('person', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalApiKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(choices=[('/api/appauth/authortools', '/api/appauth/authortools'), ('/api/appauth/bibxml', '/api/appauth/bibxml'), ('/api/iesg/position', '/api/iesg/position'), ('/api/meeting/session/video/url', '/api/meeting/session/video/url'), ('/api/notify/meeting/bluesheet', '/api/notify/meeting/bluesheet'), ('/api/notify/meeting/registration', '/api/notify/meeting/registration'), ('/api/notify/session/attendees', '/api/notify/session/attendees'), ('/api/notify/session/chatlog', '/api/notify/session/chatlog'), ('/api/notify/session/polls', '/api/notify/session/polls'), ('/api/v2/person/person', '/api/v2/person/person')], max_length=128)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid', models.BooleanField(default=True)),
                ('salt', models.BinaryField(default=ietf.person.models.salt, max_length=12)),
                ('count', models.IntegerField(default=0)),
                ('latest', models.DateTimeField(blank=True, null=True)),
                ('person', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='apikeys', to='person.Person')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalPerson',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(db_index=True, help_text='Preferred long form of name.', max_length=255, validators=[ietf.person.models.name_character_validator], verbose_name='Full Name (Unicode)')),
                ('plain', models.CharField(blank=True, default='', help_text="Use this if you have a Spanish double surname.  Don't use this for nicknames, and don't use it unless you've actually observed that the datatracker shows your name incorrectly.", max_length=64, verbose_name='Plain Name correction (Unicode)')),
                ('ascii', models.CharField(help_text='Name as rendered in ASCII (Latin, unaccented) characters.', max_length=255, verbose_name='Full Name (ASCII)')),
                ('ascii_short', models.CharField(blank=True, help_text='Example: A. Nonymous.  Fill in this with initials and surname only if taking the initials and surname of the ASCII name above produces an incorrect initials-only form. (Blank is OK).', max_length=32, null=True, verbose_name='Abbreviated Name (ASCII)')),
                ('pronouns_selectable', jsonfield.fields.JSONCharField(blank=True, default=list, max_length=120, null=True, verbose_name='Pronouns')),
                ('pronouns_freetext', models.CharField(blank=True, help_text='Optionally provide your personal pronouns. These will be displayed on your public profile page and alongside your name in Meetecho and, in future, other systems. Select any number of the checkboxes OR provide a custom string up to 30 characters.', max_length=30, null=True, verbose_name=' ')),
                ('biography', models.TextField(blank=True, help_text='Short biography for use on leadership pages. Use plain text or reStructuredText markup.')),
                ('photo', models.TextField(blank=True, default=None, max_length=100)),
                ('photo_thumb', models.TextField(blank=True, default=None, max_length=100)),
                ('name_from_draft', models.CharField(editable=False, help_text='Name as found in an Internet-Draft submission.', max_length=255, null=True, verbose_name='Full Name (from submission)')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical person',
                'verbose_name_plural': 'historical persons',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalEmail',
            fields=[
                ('address', django.contrib.postgres.fields.citext.CICharField(db_index=True, max_length=64, validators=[django.core.validators.EmailValidator()])),
                ('time', models.DateTimeField(blank=True, editable=False)),
                ('primary', models.BooleanField(default=False)),
                ('origin', models.CharField(help_text="The origin of the address: the user's email address, or 'author: DRAFTNAME' if an Internet-Draft, or 'role: GROUP/ROLE' if a role.", max_length=150)),
                ('active', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('person', ietf.utils.models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='person.Person')),
            ],
            options={
                'verbose_name': 'historical email',
                'verbose_name_plural': 'historical emails',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('address', django.contrib.postgres.fields.citext.CICharField(max_length=64, primary_key=True, serialize=False, validators=[django.core.validators.EmailValidator()])),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('primary', models.BooleanField(default=False)),
                ('origin', models.CharField(help_text="The origin of the address: the user's email address, or 'author: DRAFTNAME' if an Internet-Draft, or 'role: GROUP/ROLE' if a role.", max_length=150)),
                ('active', models.BooleanField(default=True)),
                ('person', ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('person', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
            ],
            options={
                'verbose_name_plural': 'Aliases',
            },
        ),
        migrations.AddIndex(
            model_name='personevent',
            index=models.Index(fields=['-time', '-id'], name='person_pers_time_8dfbc5_idx'),
        ),
        migrations.AddField(
            model_name='personapikeyevent',
            name='key',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.PersonalApiKey'),
        ),
    ]