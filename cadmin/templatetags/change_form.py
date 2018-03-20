#!/usr/bin/env python
# coding:utf-8
# Created by Andy @ 2018/3/20

from django.template import Library
from django.urls import reverse
from cadmin.service.cadmin import site

register = Library()

@register.inclusion_tag('cadmin/cadmin-form.html')
def form(model_form_obj):
    new_form = []
    for bfield in model_form_obj:
        temp = {'is_popup': False, 'item': bfield}
        from django.forms.boundfield import BoundField
        from django.forms.models import ModelChoiceField

        if isinstance(bfield.field, ModelChoiceField):
            relate_class_name = bfield.field.queryset.model
            if relate_class_name in site._registry:
                model_to_url = relate_class_name._meta.app_label, relate_class_name._meta.model_name
                base_url = reverse("cadmin:%s_%s_add" % model_to_url)
                print(base_url)
                popurl = "%s?_popbackid=%s" % (base_url, bfield.auto_id)
                temp['is_popup'] = True
                temp['popurl'] = popurl
        new_form.append(temp)
    return ({'form': new_form})
