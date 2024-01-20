# Copyright The IETF Trust 2014-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Autogenerated by the mkresources management command 2014-11-13 23:53


from ietf.api import ModelResource
from tastypie.fields import ToOneField
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from ietf import api

from ietf.redirects.models import Redirect, Suffix, Command


class RedirectResource(ModelResource):
    class Meta:
        cache = SimpleCache()
        queryset = Redirect.objects.all()
        serializer = api.Serializer()
        #resource_name = 'redirect'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "cgi": ALL,
            "url": ALL,
            "rest": ALL,
            "remove": ALL,
        }
api.redirects.register(RedirectResource())

class SuffixResource(ModelResource):
    class Meta:
        cache = SimpleCache()
        queryset = Suffix.objects.all()
        serializer = api.Serializer()
        #resource_name = 'suffix'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "rest": ALL,
            "remove": ALL,
        }
api.redirects.register(SuffixResource())

class CommandResource(ModelResource):
    script           = ToOneField(RedirectResource, 'script')
    suffix           = ToOneField(SuffixResource, 'suffix', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = Command.objects.all()
        serializer = api.Serializer()
        #resource_name = 'command'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "command": ALL,
            "url": ALL,
            "script": ALL_WITH_RELATIONS,
            "suffix": ALL_WITH_RELATIONS,
        }
api.redirects.register(CommandResource())

