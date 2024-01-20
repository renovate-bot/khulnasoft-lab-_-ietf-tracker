# Copyright The IETF Trust 2014-2020, All Rights Reserved
# -*- coding: utf-8 -*-

from ietf.ipr.models import IprDocRel

import debug                            # pyflakes:ignore

def get_genitive(name):
    """Return the genitive form of name"""
    return name + "'" if name.endswith('s') else name + "'s"

def get_ipr_summary(disclosure):
    """Return IPR related document names as a formatted string"""
    names = []
    for doc in disclosure.docs.all():
        if doc.name.startswith('rfc'):
            names.append('RFC {}'.format(doc.name[3:]))
        else:
            names.append(doc.name)
    
    if disclosure.other_designations:
        names.append(disclosure.other_designations)

    if not names:
        summary = ''
    elif len(names) == 1:
        summary = names[0]
    elif len(names) == 2:
        summary = " and ".join(names)
    elif len(names) > 2:
        summary = ", ".join(names[:-1]) + ", and " + names[-1]
    return summary if len(summary) <= 128 else summary[:125]+'...'


def iprs_from_docs(docs,**kwargs):
    """Returns a list of IPRs related to docs"""
    iprdocrels = []
    for document in docs:
        if document.ipr(**kwargs):
            iprdocrels += document.ipr(**kwargs)
    return list(set([i.disclosure for i in iprdocrels]))
    
def related_docs(doc, relationship=('replaces', 'obs'), reverse_relationship=("became_rfc",)):
    """Returns list of related documents"""

    results = [doc]

    rels = doc.all_relations_that_doc(relationship)

    for rel in rels:
        rel.target.related = rel
        rel.target.relation = rel.relationship.revname
    results += [x.target for x in rels]

    rev_rels = doc.all_relations_that(reverse_relationship)
    for rel in rev_rels:
        rel.source.related = rel
        rel.source.relation = rel.relationship.name
    results += [x.source for x in rev_rels]

    return list(set(results))


def generate_draft_recursive_txt():
    docipr = {}

    for o in IprDocRel.objects.filter(disclosure__state='posted').select_related('document'):
        doc = o.document
        name = doc.name
        related_set = set(doc) | set(doc.all_related_that_doc(('obs', 'replaces')))
        for related in related_set:
            name = related.name
            if name.startswith("rfc"):
                name = name.upper()
            if not name in docipr:
                docipr[name] = []
            docipr[name].append(o.disclosure_id)

    lines = [ "# Machine-readable list of IPR disclosures by Internet-Draft name" ]
    for name, iprs in docipr.items():
        lines.append(name + "\t" + "\t".join(str(ipr_id) for ipr_id in sorted(iprs)))

    data = '\n'.join(lines)
    filename = '/a/ietfdata/derived/ipr_draft_recursive.txt'
    with open(filename, 'w') as f:
        f.write(data)

    
