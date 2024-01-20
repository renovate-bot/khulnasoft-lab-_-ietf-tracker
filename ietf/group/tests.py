# Copyright The IETF Trust 2013-2020, All Rights Reserved
# -*- coding: utf-8 -*-

import io
import os
import datetime
import json

from tempfile import NamedTemporaryFile

from django.core.management import call_command
from django.conf import settings
from django.urls import reverse as urlreverse
from django.db.models import Q
from django.test import Client
from django.utils import timezone

import debug                             # pyflakes:ignore

from ietf.doc.factories import DocumentFactory, WgDraftFactory, EditorialDraftFactory
from ietf.doc.models import DocEvent, RelatedDocument, Document
from ietf.group.models import Role, Group
from ietf.group.utils import get_group_role_emails, get_child_group_role_emails, get_group_ad_emails
from ietf.group.factories import GroupFactory, RoleFactory
from ietf.person.factories import PersonFactory, EmailFactory
from ietf.person.models import Person
from ietf.utils.test_utils import login_testing_unauthorized, TestCase

class StreamTests(TestCase):
    def test_streams(self):
        r = self.client.get(urlreverse("ietf.group.views.streams"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Independent Submission Editor")

    def test_stream_documents(self):
        draft = DocumentFactory(type_id='draft',group__acronym='iab',states=[('draft','active')])
        draft.stream_id = "iab"
        draft.save_with_history([DocEvent.objects.create(doc=draft, rev=draft.rev, type="changed_stream", by=Person.objects.get(user__username="secretary"), desc="Test")])

        r = self.client.get(urlreverse("ietf.group.views.stream_documents", kwargs=dict(acronym="iab")))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, draft.name)

        EditorialDraftFactory() # Quick way to ensure RSWG exists.
        r = self.client.get(urlreverse("ietf.group.views.stream_documents", kwargs=dict(acronym="editorial")))
        self.assertRedirects(r, expected_url=urlreverse('ietf.group.views.group_documents',kwargs={"acronym":"rswg"}))


    def test_stream_edit(self):
        EmailFactory(address="ad2@ietf.org")

        stream_acronym = "ietf"

        url = urlreverse("ietf.group.views.stream_edit", kwargs=dict(acronym=stream_acronym))
        login_testing_unauthorized(self, "secretary", url)

        # get
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        r = self.client.post(url, dict(delegates="ad2@ietf.org"))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Role.objects.filter(name="delegate", group__acronym=stream_acronym, email__address="ad2@ietf.org"))


class GroupStatsTests(TestCase):
    def setUp(self):
        super().setUp()
        a = WgDraftFactory()
        b = WgDraftFactory()
        RelatedDocument.objects.create(
            source=a, target=b, relationship_id="refnorm"
        )

    def test_group_stats(self):
        client = Client(Accept="application/json")
        url = urlreverse("ietf.group.views.group_stats_data")
        r = client.get(url)
        self.assertTrue(r.status_code == 200, "Failed to receive group stats")
        self.assertGreater(len(r.content), 0, "Group stats have no content")

        try:
            data = json.loads(r.content)
        except Exception as e:
            self.fail("JSON load failed: %s" % e)

        ids = [d["id"] for d in data]
        for doc in Document.objects.all():
            self.assertIn(doc.name, ids)


class GroupDocDependencyTests(TestCase):
    def setUp(self):
        super().setUp()
        a = WgDraftFactory()
        b = WgDraftFactory()
        RelatedDocument.objects.create(
            source=a, target=b, relationship_id="refnorm"
        )

    def test_group_document_dependencies(self):
        for group in Group.objects.filter(Q(type="wg") | Q(type="rg")):
            client = Client(Accept="application/json")
            for url in [
                urlreverse(
                    "ietf.group.views.dependencies", kwargs=dict(acronym=group.acronym)
                ),
                urlreverse(
                    "ietf.group.views.dependencies",
                    kwargs=dict(acronym=group.acronym, group_type=group.type_id),
                ),
            ]:
                r = client.get(url)
                self.assertTrue(
                    r.status_code == 200,
                    "Failed to receive a group document dependencies for group: %s"
                    % group.acronym,
                )
                self.assertGreater(
                    len(r.content),
                    0,
                    "Document dependencies for group %s has no content" % group.acronym,
                )
                try:
                    json.loads(r.content)
                except Exception as e:
                    self.fail("JSON load failed: %s" % e)


class GenerateGroupAliasesTests(TestCase):
    def setUp(self):
        super().setUp()
        self.doc_aliases_file = NamedTemporaryFile(delete=False, mode='w+')
        self.doc_aliases_file.close()
        self.doc_virtual_file = NamedTemporaryFile(delete=False, mode='w+')
        self.doc_virtual_file.close()
        self.saved_draft_aliases_path = settings.GROUP_ALIASES_PATH
        self.saved_draft_virtual_path = settings.GROUP_VIRTUAL_PATH
        settings.GROUP_ALIASES_PATH = self.doc_aliases_file.name
        settings.GROUP_VIRTUAL_PATH = self.doc_virtual_file.name
        
    def tearDown(self):
        settings.GROUP_ALIASES_PATH = self.saved_draft_aliases_path
        settings.GROUP_VIRTUAL_PATH = self.saved_draft_virtual_path
        os.unlink(self.doc_aliases_file.name)
        os.unlink(self.doc_virtual_file.name)
        super().tearDown()

    def testManagementCommand(self):
        a_month_ago = timezone.now() - datetime.timedelta(30)
        a_decade_ago = timezone.now() - datetime.timedelta(3650)
        role1 = RoleFactory(name_id='ad', group__type_id='area', group__acronym='myth', group__state_id='active')
        area = role1.group
        ad = role1.person
        mars = GroupFactory(type_id='wg', acronym='mars', parent=area)
        marschair = PersonFactory(user__username='marschair')
        mars.role_set.create(name_id='chair', person=marschair, email=marschair.email())
        marssecr = PersonFactory(user__username='marssecr')
        mars.role_set.create(name_id='secr', person=marssecr, email=marssecr.email())
        ames = GroupFactory(type_id='wg', acronym='ames', parent=area)
        ameschair = PersonFactory(user__username='ameschair')
        ames.role_set.create(name_id='chair', person=ameschair, email=ameschair.email())
        recent = GroupFactory(type_id='wg', acronym='recent', parent=area, state_id='conclude', time=a_month_ago)
        recentchair = PersonFactory(user__username='recentchair')
        recent.role_set.create(name_id='chair', person=recentchair, email=recentchair.email())
        wayold = GroupFactory(type_id='wg', acronym='recent', parent=area, state_id='conclude', time=a_decade_ago)
        wayoldchair = PersonFactory(user__username='wayoldchair')
        wayold.role_set.create(name_id='chair', person=wayoldchair, email=wayoldchair.email())
        role2 = RoleFactory(name_id='ad', group__type_id='area', group__acronym='done', group__state_id='conclude')
        done = role2.group
        done_ad = role2.person
        irtf = Group.objects.get(acronym='irtf')
        testrg = GroupFactory(type_id='rg', acronym='testrg', parent=irtf)
        testrgchair = PersonFactory(user__username='testrgchair')
        testrg.role_set.create(name_id='chair', person=testrgchair, email=testrgchair.email())
        testrag = GroupFactory(type_id='rg', acronym='testrag', parent=irtf)
        testragchair = PersonFactory(user__username='testragchair')
        testrag.role_set.create(name_id='chair', person=testragchair, email=testragchair.email())
        individual = PersonFactory()

        args = [ ]
        kwargs = { }
        out = io.StringIO()
        call_command("generate_group_aliases", *args, **kwargs, stdout=out, stderr=out)
        self.assertFalse(out.getvalue())

        with open(settings.GROUP_ALIASES_PATH) as afile:
            acontent = afile.read()
            self.assertTrue('xfilter-' + area.acronym + '-ads' in acontent)
            self.assertTrue('xfilter-' + area.acronym + '-chairs' in acontent)
            self.assertTrue('xfilter-' + mars.acronym + '-ads' in acontent)
            self.assertTrue('xfilter-' + mars.acronym + '-chairs' in acontent)
            self.assertTrue('xfilter-' + ames.acronym + '-ads' in acontent)
            self.assertTrue('xfilter-' + ames.acronym + '-chairs' in acontent)
            self.assertTrue(all([x in acontent for x in [
                'xfilter-' + area.acronym + '-ads',
                'xfilter-' + area.acronym + '-chairs',
                'xfilter-' + mars.acronym + '-ads',
                'xfilter-' + mars.acronym + '-chairs',
                'xfilter-' + ames.acronym + '-ads',
                'xfilter-' + ames.acronym + '-chairs',
                'xfilter-' + recent.acronym + '-ads',
                'xfilter-' + recent.acronym + '-chairs',
            ]]))
            self.assertFalse(all([x in acontent for x in [
                'xfilter-' + done.acronym + '-ads',
                'xfilter-' + done.acronym + '-chairs',
                'xfilter-' + wayold.acronym + '-ads',
                'xfilter-' + wayold.acronym + '-chairs',
            ]]))

        with open(settings.GROUP_VIRTUAL_PATH) as vfile:
            vcontent = vfile.read()
            self.assertTrue(all([x in vcontent for x in [
                ad.email_address(),
                marschair.email_address(),
                marssecr.email_address(),
                ameschair.email_address(),
                recentchair.email_address(),
                testrgchair.email_address(),
                testragchair.email_address(),
            ]]))
            self.assertFalse(all([x in vcontent for x in [
                done_ad.email_address(),
                wayoldchair.email_address(),
                individual.email_address(),
            ]]))
            self.assertTrue(all([x in vcontent for x in [
                'xfilter-' + area.acronym + '-ads',
                'xfilter-' + area.acronym + '-chairs',
                'xfilter-' + mars.acronym + '-ads',
                'xfilter-' + mars.acronym + '-chairs',
                'xfilter-' + ames.acronym + '-ads',
                'xfilter-' + ames.acronym + '-chairs',
                'xfilter-' + recent.acronym + '-ads',
                'xfilter-' + recent.acronym + '-chairs',
                'xfilter-' + testrg.acronym + '-chairs',
                'xfilter-' + testrag.acronym + '-chairs',
                testrg.acronym + '-chairs@ietf.org',
                testrg.acronym + '-chairs@irtf.org',
                testrag.acronym + '-chairs@ietf.org',
                testrag.acronym + '-chairs@irtf.org',
            ]]))
            self.assertFalse(all([x in vcontent for x in [
                'xfilter-' + done.acronym + '-ads',
                'xfilter-' + done.acronym + '-chairs',
                'xfilter-' + wayold.acronym + '-ads',
                'xfilter-' + wayold.acronym + '-chairs',
            ]]))


class GroupRoleEmailTests(TestCase):
    
    def setUp(self):
        super().setUp()
        # make_immutable_base_data makes two areas, and puts a group in one of them
        # the tests below assume all areas have groups
        for area in Group.objects.filter(type_id='area'):
            for iter_count in range(2):
                group = GroupFactory(type_id='wg',parent=area)
                RoleFactory(group=group,name_id='chair',person__user__email='{%s}chairman@ietf.org'%group.acronym)
                RoleFactory(group=group,name_id='secr',person__user__email='{%s}secretary@ietf.org'%group.acronym)

    def test_group_role_emails(self):
        wgs = Group.objects.filter(type='wg')
        for wg in wgs:
            chair_emails = get_group_role_emails(wg, ['chair'])
            secr_emails  = get_group_role_emails(wg, ['secr'])
            self.assertIn("chairman", list(chair_emails)[0])
            self.assertIn("secretary", list(secr_emails)[0])
            both_emails  = get_group_role_emails(wg, ['chair', 'secr'])
            self.assertEqual(secr_emails | chair_emails, both_emails)

    def test_child_group_role_emails(self):
        areas = Group.objects.filter(type='area')
        for area in areas:
            emails = get_child_group_role_emails(area, ['chair', 'secr'])
            self.assertGreater(len(emails), 0)
            for item in emails:
                self.assertIn('@', item)

    def test_group_ad_emails(self):
        wgs = Group.objects.filter(type='wg')
        for wg in wgs:
            emails = get_group_ad_emails(wg)
            self.assertGreater(len(emails), 0)
            for item in emails:
                self.assertIn('@', item)
