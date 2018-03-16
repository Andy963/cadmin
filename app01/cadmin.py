#!/usr/bin/env python
# coding:utf-8
# Created by Andy @ 2018/3/13


from django.shortcuts import HttpResponse, render, redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf.urls import url
from django.forms import ModelForm
from cadmin.service import cadmin
from app01 import models


class UserConfig(cadmin.CadminConfig):
    list_display = ['id', 'name', 'age', ]


class BookConfig(cadmin.CadminConfig):
    list_display = ['id', 'name']
    search_fields = ["name", ]
    show_add_btn = True


class HostModelForm(ModelForm):
    """
    custom Host model
    """
    class Meta:
        model = models.Host
        fields = ['id', 'hostname', 'ip', 'port']
        error_messages = {
            'hostname': {
                'required': '主机名不能为空',
            },
            'ip': {
                'required': 'IP不能为空',
                'invalid': 'IP格式错误',
            }

        }


class HostConfig(cadmin.CadminConfig):
    model_form_class = HostModelForm



    def ip_port(self, obj=None, is_header=False):
        """
        custom method to show in html
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return '自定义列'
        return "%s:%s" % (obj.ip, obj.port,)

    def extra_url(self):
        urls = [
            url('^report/$', self.report_view)
        ]
        return urls

    def report_view(self, request):
        pass

    # refactor the cadminConfig function delete view
    def delete_view(self, request,id, *args, **kwargs):
        """
        when click delete button redirect to the delete view to check if you really want ot delete items!
        :param request:
        :param id:
        :param args:
        :param kwargs:
        :return:
        """
        if request.method == 'GET':
            return render(request, 'cadmin/delete_view.html')
        else:
            self.model_class.objects.filter(pk=id).delete()
            return redirect(self.get_search_url())


    list_display = ['ip', 'port', ip_port]


cadmin.site.register(models.User, UserConfig)
cadmin.site.register(models.Book, BookConfig)
cadmin.site.register(models.Host, HostConfig)
