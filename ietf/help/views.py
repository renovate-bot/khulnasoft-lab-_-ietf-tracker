# Copyright The IETF Trust 2007, All Rights Reserved

from django.shortcuts import get_object_or_404, render

import debug                            # pyflakes:ignore

from ietf.doc.models import State, StateType
from ietf.name.models import StreamName

def state_index(request):
    types = StateType.objects.all()
    names = [ type.slug for type in types ]
    for type in types:
        if "-" in type.slug and type.slug.split('-',1)[0] in names:
            type.stategroups = None
        else:
            groups = StateType.objects.filter(slug__startswith=type.slug)
            type.stategroups =  [ g.slug[len(type.slug)+1:] for g in groups if not g == type ] or ""
                
    return render(request, 'help/state_index.html', {"types": types})

def state(request, doc, type=None):
    if type:
        streams = [ s.slug for s in StreamName.objects.all() ]
        if type in streams:
            type = "stream-%s" % type
    slug = "%s-%s" % (doc,type) if type else doc
    statetype = get_object_or_404(StateType, slug=slug)
    states = State.objects.filter(used=True, type=statetype).order_by('order')
    return render(request, 'help/states.html', {"doc": doc, "type": statetype, "states":states} )
