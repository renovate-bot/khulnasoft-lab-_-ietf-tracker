# Copyright The IETF Trust 2012-2020, All Rights Reserved
# -*- coding: utf-8 -*-


import datetime
import io
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import debug                            # pyflakes:ignore

from ietf.doc.models import NewRevisionDocEvent
from ietf.doc.utils import bibxml_for_draft

DEFAULT_DAYS = 7

class Command(BaseCommand):
    help = ('Generate draft bibxml files for xml2rfc references, placing them in the '
            'directory configured in settings.BIBXML_BASE_PATH: %s.  '
            'By default, generate files as needed for new Internet-Draft revisions from the '
            'last %s days.' % (settings.BIBXML_BASE_PATH, DEFAULT_DAYS))

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', default=False, help="Process all documents, not only recent submissions")
        parser.add_argument('--days', type=int, default=DEFAULT_DAYS, help="Look submissions from the last DAYS days, instead of %s" % DEFAULT_DAYS)

    def say(self, msg):
        if self.verbosity > 0:
            sys.stdout.write(msg)
            sys.stdout.write('\n')

    def note(self, msg):
        if self.verbosity > 1:
            sys.stdout.write(msg)
            sys.stdout.write('\n')

    def mutter(self, msg):
        if self.verbosity > 2:
            sys.stdout.write(msg)
            sys.stdout.write('\n')

    def write(self, fn, new):
        # normalize new
        new = re.sub(r'\r\n?', r'\n', new)
        try:
            with io.open(fn, encoding='utf-8') as f:
                old = f.read()
        except IOError:
            old = ""
        if old.strip() != new.strip():
            self.note('Writing %s' % os.path.basename(fn))
            with io.open(fn, "w", encoding='utf-8') as f:
                f.write(new)

    def handle(self, *args, **options):
        self.verbosity = options.get("verbosity", 1)
        process_all = options.get("all")
        days = options.get("days")
        #
        bibxmldir = os.path.join(settings.BIBXML_BASE_PATH, 'bibxml-ids')
        if not os.path.exists(bibxmldir):
            os.makedirs(bibxmldir)
        #
        if process_all:
            doc_events = NewRevisionDocEvent.objects.filter(type='new_revision', doc__type_id='draft')
        else:
            start = timezone.now() - datetime.timedelta(days=days)
            doc_events = NewRevisionDocEvent.objects.filter(type='new_revision', doc__type_id='draft', time__gte=start)
        doc_events = doc_events.order_by('time')

        for e in doc_events:
            self.mutter('%s %s' % (e.time, e.doc.name))
            try:
                doc = e.doc
                bibxml = bibxml_for_draft(doc, e.rev)
                ref_rev_file_name = os.path.join(bibxmldir, 'reference.I-D.%s-%s.xml' % (doc.name, e.rev))
                self.write(ref_rev_file_name, bibxml)
            except Exception as ee:
                sys.stderr.write('\n%s-%s: %s\n' % (doc.name, doc.rev, ee))
