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

    actions = ['mutil_del', 'mutil_initial']


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
    def delete_view(self, request, id, *args, **kwargs):
        """
        when click delete button redirect to the delete view to check if you really want ot delete items!
        """
        if request.method == 'GET':
            return render(request, 'cadmin/delete_view.html')
        else:
            self.model_class.objects.filter(pk=id).delete()
            return redirect(self.get_search_url())

    list_display = ['ip', 'port', ip_port]

class RoleConfig(cadmin.CadminConfig):
    list_display = ['id','title']
    show_add_btn = True

class DepartmentConfig(cadmin.CadminConfig):
    list_display = ['id','caption']
    show_add_btn = True

class UserInfoConfig(cadmin.CadminConfig):

    def display_gender(self, obj=None, is_header=False):
        # show choice field value but not the short key
        if is_header:
            return 'gender'
        return obj.get_gender_display() # gender is a choice field use get_field_display to get choices

    def display_roles(self,obj=None, is_header=False):
        # role is Many2many field, object.role.all to get all of the role of the obj, then do loop add to a list to show in html
        if is_header:
            return 'role'

        show_role = []
        roles = obj.role.all()
        for role in roles:
            show_role.append(role.title)
        return ','.join(show_role)

    # combine_filter = ['gender','depart','role'], when we choose different condition we should conbine it to filter
    # and we need to check if it's a choice field or one2many many2many field
    combine_filter =[
        cadmin.FilterOption('gender', is_choice=True),
        cadmin.FilterOption('depart'),
        cadmin.FilterOption('role',True),
    ]


    # we difined the display_gender, display_roles function to show choice field, many2many field 
    # TODO: we can set a default display fucntion in cadmin , when we need to do this just herit from it , or overwrite ti
    list_display = ['name','email', display_gender,'depart', display_roles]

    show_add_btn = True # add new userinfo button

class UserTypeConfig(cadmin.CadminConfig):
    list_display = ['type'  ]
    show_add_btn = True


cadmin.site.register(models.User, UserConfig)
cadmin.site.register(models.Book, BookConfig)
cadmin.site.register(models.Host, HostConfig)
cadmin.site.register(models.Role, RoleConfig)
cadmin.site.register(models.Department, DepartmentConfig)
cadmin.site.register(models.UserInfo, UserInfoConfig)
cadmin.site.register(models.UserType, UserTypeConfig)
