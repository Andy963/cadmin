#!/usr/bin/env python
# coding:utf-8
# Created by Andy @ 2018/3/13


from django.forms import ModelForm
from django.conf.urls import url, include
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe


class Show(object):
    def __init__(self, config, request, all_objects):
        self.request = request
        self.config = config
        self.all_objects = all_objects

        current_page = self.request.GET.get("page", 1)
        base_url = self.request.path_info
        params = self.request.GET

        total_count = self.all_objects.count()
        from cadmin.utils.pager import Pagination
        pagination = Pagination(current_page, total_count, base_url, params, items_per_page=5, max_pages_count=11)
        self.pagination = pagination
        data_list = self.all_objects[self.pagination.start:self.pagination.end]
        self.data_list = data_list

        page_html = pagination.page_html()

    def get_header(self):
        header_list = []
        for field_name in self.config.get_list_display():

            if isinstance(field_name, str):
                verbose_name = self.config.model_class._meta.get_field(field_name).verbose_name
            else:
                # field_name here is a function, field_name() call the function in cadmin.UserConfig
                verbose_name = field_name(self.config, is_header=True)  # edit(self, is_header=True)
            header_list.append(verbose_name)
        return header_list

    def get_body(self):
        new_data_list = []
        for object in self.data_list:

            temp = []
            for field_name in self.config.get_list_display():
                if isinstance(field_name, str):  # callable(field_name)
                    val = getattr(object, field_name)  # get the obj's value of field field_name (user's name)
                else:
                    val = field_name(self.config, object)  # edit self --> BookConfig.edit get from own class first
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list


class CadminConfig(object):
    """
    This is the default admin config, if you don't set a custom config in your cadmin.py, this
    conifg will work.
    In cadmin.py eg: cadmin.site.register(Book), in CadminSite.regsiter(self, model_class, cadmin_config_class=None)
    the cadmin_config_class will set to CadminConfig
    """

    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site

    search_fields = []

    def get_urls(self):
        """
        get urls of add, delete, modify, search urls
        :return: url_patterns
        """
        app_label, app_model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        # app_label= app name like cadmin, app_model_name = model name like user
        url_patterns = [
            url(r'^$', self.search_view, name="%s_%s_search" % (app_label, app_model_name)),
            url(r'^add/$', self.add_view, name="%s_%s_add" % (app_label, app_model_name)),
            url(r'^modify/(?P<id>\d+)/$', self.modify_view, name="%s_%s_modify" % (app_label, app_model_name)),
            url(r'^delete/(?P<id>\d+)/$', self.delete_view, name="%s_%s_delete" % (app_label, app_model_name)),
        ]
        return url_patterns

    @property
    # we can visit the urls by dot , but can not set urls by =
    def urls(self):
        """
        make get_urls as a static method
        :return: self.get_urls
        """
        return self.get_urls()

    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return mark_safe('<input type="checkbox"  id="choose" />')
        return mark_safe('<input type="checkbox" name="pk" value="%s" />' % (obj.id,))

    def modify(self, obj=None, is_header=False):
        if is_header:
            return 'Modify'
        # temp_url = "cadmin:%s_%s_modify" %(self.model_class._meta.app_label, self.model_class._meta.model_name)
        # edit_url = reverse(temp_url, args=(obj.id,))
        return mark_safe('<a href="%s">modify</a>' % (self.get_modify_url(obj.id),))

    def delete(self, obj=None, is_header=False):
        if is_header:
            return 'Delete'
        return mark_safe('<a href="%s">delete</a>' % (self.get_delete_url(obj.id),))

    list_display = []

    def get_list_display(self):
        new_list_display = []
        if self.list_display:
            new_list_display.extend(self.list_display)
            new_list_display.append(CadminConfig.modify)
            new_list_display.append(CadminConfig.delete)
            new_list_display.insert(0, CadminConfig.checkbox)
            return new_list_display

    model_form_class = None

    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_class

        class TestModelForm(ModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"

        # meta = type("Meta", (object,),{'model':self.model_class, 'fields':'__all__'})
        # TestModelForm = type('TestModelForm',(ModelForm,), {'Meta':meta})
        return TestModelForm

    # get reversed modify_url
    # Be careful: no space between cadmin and %s_%s_delete
    def get_modify_url(self, nid):
        temp_url = "cadmin:%s_%s_modify" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        modify_url = reverse(temp_url, args=(nid,))
        return modify_url

    def get_add_url(self):
        temp_url = "cadmin:%s_%s_add" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        add_url = reverse(temp_url, )
        return add_url

    def get_search_url(self):
        temp_url = "cadmin:%s_%s_search" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        search_url = reverse(temp_url)
        return search_url

    # get reversed delete_url
    def get_delete_url(self, nid):
        temp_url = "cadmin:%s_%s_delete" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        delete_url = reverse(temp_url, args=(nid,))
        return delete_url

    show_add_btn = False

    def get_show_add_btn(self):
        return self.show_add_btn

    def search_view(self, request):
        self.request = request
        search_condition = self.get_search_condition()
        all_objects = self.model_class.objects.filter(search_condition)
        show_page = Show(self, request, all_objects)
        add_url = self.get_add_url()
        show_add_btn = self.get_show_add_btn()
        context = {
            'show_page': show_page,
            'add_url': add_url,
            'show_add_btn': show_add_btn,

        }
        return render(request, 'cadmin/show_view.html', context)

    def add_view(self, request, *args, **kwargs):
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class()
            return render(request, 'cadmin/add_view.html', {'form': form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_search_url(), )
            return render(request, 'cadmin/add_view.html', {'form': form})
            # form = AddModelForm

    def modify_view(self, request, id, *args, **kwargs):
        obj = self.model_class.objects.filter(pk=id).first()
        if not obj:
            return redirect(self.get_search_url())
        model_form_class = self.get_model_form_class()
        if request.method == 'GET':
            form = model_form_class(instance=obj)
            return render(request, 'cadmin/modify_view.html', {'form': form})
        else:
            form = model_form_class(instance=obj, data=request.POST)
            if form.is_valid():
                return redirect(self.get_search_url())
            return render(request, 'cadmin/modify_view.html', {'form': form})

    def delete_view(self, request, id, *args, **kwargs):
        self.model_class.objects.filter(pk=id).delete()
        return redirect(self.get_search_url())

    def get_link_tag(self, obj, val):
        params = self.request.GET
        import copy
        params = copy.deepcopy(params)
        params._mutable = True

        from django.http import QueryDict

        qd = QueryDict(mutable=True)

        qd["list_filter"] = params.urlencode()  # qd: {"list_filter":"a%21341%1234b%21322"}

        s = mark_safe("<a href='%s?%s'>%s</a>" % (self.get_modify_url(obj), qd.urlencode(), val))

        return s

    def get_search_condition(self):
        from django.db.models import Q
        search_condition = Q()
        search_condition.connector = "or"
        if self.search_fields:
            key_word = self.request.GET.get("q")
            if key_word:
                for search_field in self.search_fields:
                    search_condition.children.append((search_field + "__contains", key_word))

        return search_condition


class CadminSite(object):
    def __init__(self):
        self._registry = {}

    def register(self, model_class, cadmin_config_class=None):
        """
        register a model and it's admin
        eg: self._registry[User] = UserConfig(self, User) --> {User: UserConfig}  <==> {Book: Bookadmin}
        UserConfig is the class up cadminConfig

        :param model_class: model to register
        :param cadmin_config_class: model's admin
        :return:
        """
        if not cadmin_config_class:
            cadmin_config_class = CadminConfig
        self._registry[model_class] = cadmin_config_class(model_class, self)

    def get_urls(self):
        url_pattern = []
        for model_class, cadmin_config_obj in self._registry.items():  # {User: UserConfig}
            app_name, model_name = model_class._meta.app_label, model_class._meta.model_name

            model_url = url(r'^%s/%s/' % (app_name, model_name,), (cadmin_config_obj.urls, None, None))
            # UserConfig <-- CadminConfig ---> User.urls---> get all of the urls from CadminConfig
            url_pattern.append(model_url)
        return url_pattern

    @property
    def urls(self):
        return (self.get_urls(), None, 'cadmin')

        # Instance of CadminSite


site = CadminSite()
