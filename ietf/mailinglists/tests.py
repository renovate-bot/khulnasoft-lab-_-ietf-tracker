# Copyright The IETF Trust 2009-2020, All Rights Reserved
# -*- coding: utf-8 -*-


from pyquery import PyQuery

from django.urls import reverse as urlreverse

import debug                            # pyflakes:ignore

from ietf.group.factories import GroupFactory
from ietf.mailinglists.factories import ListFactory
from ietf.utils.test_utils import TestCase


class MailingListTests(TestCase):
    def test_groups(self):
        url = urlreverse("ietf.mailinglists.views.groups")

        # only those with an archive
        group = GroupFactory()
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("#content a:contains(\"%s\")" % group.acronym)), 0)

        # successful get
        group = GroupFactory(list_archive = "https://example.com/foo")
        r = self.client.get(url)
        q = PyQuery(r.content)
        self.assertEqual(len(q("#content a:contains(\"%s\")" % group.acronym)), 1)


    def test_nonwg(self):
        groups = list()
        groups.append(GroupFactory(type_id='wg', acronym='mars', list_archive='https://ietf.org/mars'))
        groups.append(GroupFactory(type_id='wg', acronym='ames', state_id='conclude', list_archive='https://ietf.org/ames'))
        groups.append(GroupFactory(type_id='wg', acronym='newstuff', state_id='bof', list_archive='https://ietf.org/newstuff'))
        groups.append(GroupFactory(type_id='rg', acronym='research', list_archive='https://irtf.org/research'))
        lists = ListFactory.create_batch(7)

        url = urlreverse("ietf.mailinglists.views.nonwg")

        r = self.client.get(url)
        for l in lists:
            if l.advertised:
                self.assertContains(r, l.name)
                self.assertContains(r, l.description)
            else:
                self.assertNotContains(r, l.name, html=True)
                self.assertNotContains(r, l.description, html=True)

        for g in groups:
            self.assertNotContains(r, g.acronym, html=True)
