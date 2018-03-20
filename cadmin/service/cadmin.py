#!/usr/bin/env python
# coding:utf-8
# Created by Andy @ 2018/3/13


from django.forms import ModelForm
from django.conf.urls import url, include
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import QueryDict
import copy


class Show(object):
    """
    render the data to show the table header , table in html
    """

    def __init__(self, config, request, all_objects):
        self.request = request
        self.config = config
        self.all_objects = all_objects
        self.actions = config.get_actions()

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
        """
        Get the table header
        :return:
        """
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
        """
        render the data in the table to show
        :return:
        """
        new_data_list = []
        for object in self.data_list:

            temp = []
            for field_name in self.config.get_list_display():
                if isinstance(field_name, str):  # callable(field_name)
                    val = getattr(object, field_name)  # get the obj's value of field field_name (user's name)
                    if field_name in self.config.list_display_links:
                        val = self.config.get_link_tag(object, val)
                else:
                    val = field_name(self.config, object)  # edit self --> BookConfig.edit get from own class first
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list

    def show_actions(self):
        """
        format a function with name and some short_desc to show in html eg: chinese desc
        :return:
        """
        result = []
        for func in self.actions:
            temp = {'name': func.__name__, 'short_desc': func.short_desc}
            result.append(temp)
        return result


class FilterOption(object):
     # config of filter
    def __init__(self, field_name, multi=False, condition=None, is_choice=False):
        self.field_name = field_name
        self.multi = multi
        self.is_choice = is_choice
        self.condition = condition

    def get_queryset(self, _field):
        # if condition we should filter it
        if self.condition:
            return _field.rel.to.objects.filter(self.condition) # filter related objects with condition
        return _field.rel.to.objects.all()

    def get_choices(self, _field):
        # check all of the choice in a choice field
        return _field.choices

class FilterRow(object):
    # one row of combination filter
    def __init__(self, option,data, request):
        self.data = data
        self.option = option # todo: what option means here
        self.request = request # use to get the current url

    def __iter__(self):
        params = copy.deepcopy(self.request.GET)
        params._mutable = True
        current_id = params.get(self.option.field_name)
        current_id_list = params.getlist(self.option.field_name) #multiple value use getlist

        if self.option.field_name in params:
            origin_list = params.pop(self.option.field_name)
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe('<a href="{0}">all</a>'.format(url))
            params.setlist(self.option.field_name, origin_list)
        else:
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe('<a class="active" href="{0}">all</a>'.format(url))
        for val in self.data:
            if self.option.is_choice:
                pk, text = str(val[0]), val[1]
            else:
                pk, text = str(val.pk), str(val)
            if not self.option.multi:
                params[self.option.field_name] = pk
                url = "{0}?{1}".format(self.request.path_info, params.urlencode())
                if current_id == pk:
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))
                else:
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))

            else:
                _params = copy.deepcopy(params)
                id_list = _params.getlist(self.option.field_name)

                if pk in current_id_list:
                    id_list.remove(pk)
                    _params.setlist(self.option.field_name, id_list)
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    yield  mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))
                else:

                    id_list.append(pk)

                    _params.setlist(self.option.field_name, id_list)
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    yield mark_safe("<a  href='{0}'>{1}</a>".format(url, text))



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
        self.request = None
        self.params_query_key = '_list_filter'

    search_fields = []
    list_display_links = []

    def wrap(self, func):
        """
        Add request for every view
        """

        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner

    def get_urls(self):
        """
        get urls of add, delete, modify, search urls
        :return: url_patterns
        """
        app_label, app_model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        # app_label= app name like cadmin, app_model_name = model name like user
        url_patterns = [
            url(r'^$', self.wrap(self.search_view), name="%s_%s_search" % (app_label, app_model_name)),
            url(r'^add/$', self.wrap(self.add_view), name="%s_%s_add" % (app_label, app_model_name)),
            url(r'^modify/(?P<id>\d+)/$', self.wrap(self.modify_view),
                name="%s_%s_modify" % (app_label, app_model_name)),
            url(r'^delete/(?P<id>\d+)/$', self.wrap(self.delete_view),
                name="%s_%s_delete" % (app_label, app_model_name)),
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
        """
        Add a checkbox for select items in table
        :return:
        """
        if is_header:
            return mark_safe('<input type="checkbox"  id="choose" />')
        return mark_safe('<input type="checkbox" name="pk" value="%s" />' % (obj.id,))

    def modify(self, obj=None, is_header=False):
        """
        Add modify(edit) url in table action
        """
        if is_header:
            return 'Modify'

        query_str = self.request.GET.urlencode()
        if query_str:
            params = QueryDict(mutable=True)
            params[self.params_query_key] = query_str
            return mark_safe('<a href="%s?%s">modify</a>' % (self.get_modify_url(obj.id), params.urlencode(),))
        return mark_safe('<a href="%s">编辑</a>' % (self.get_modify_url(obj.id),))

    def delete(self, obj=None, is_header=False):
        """
        delete action in table
        """
        if is_header:
            return 'Delete'
        return mark_safe('<a href="%s">delete</a>' % (self.get_delete_url(obj.id),))

    list_display = []

    def get_list_display(self):
        """
        get the columns to show in the table if there is some action like modify delete
        """
        new_list_display = []
        new_list_display.extend(self.list_display)
        if not self.list_display_links:
            new_list_display.append(CadminConfig.modify)
            new_list_display.append(CadminConfig.delete)
            new_list_display.insert(0, CadminConfig.checkbox)
            return new_list_display

    model_form_class = None

    def get_model_form_class(self):
        """
        get the current model
        """
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
        """
        get modify url for the modify view to reverse
        """
        temp_url = "cadmin:%s_%s_modify" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        modify_url = reverse(temp_url, args=(nid,))
        return modify_url

    def get_add_url(self):
        """
        get add url for the add view to reverse
        """
        temp_url = "cadmin:%s_%s_add" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        add_url = reverse(temp_url, )
        return add_url

    def get_search_url(self):
        """
        get the search url for show all view (the default)
        """
        temp_url = "cadmin:%s_%s_search" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        search_url = reverse(temp_url)
        return search_url

    # get reversed delete_url
    def get_delete_url(self, nid):
        """
        get delete url for delete view
        """
        temp_url = "cadmin:%s_%s_delete" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        delete_url = reverse(temp_url, args=(nid,))
        return delete_url

    show_add_btn = False

    def get_show_add_btn(self):
        """
        get whether show the add btn or not
        :return:
        """
        return self.show_add_btn

    actions = []

    def get_actions(self):
        # get the custom actions
        result = []
        new_actions = []
        if self.actions:
            for action in self.actions:
                if isinstance(action, str):  # this makes add action's name str in action [] in admin
                    action = getattr(self, action)
                new_actions.append(action)
            result.extend(new_actions)
        return result

    def mutil_del(self, request):
        """
        delete multiple items which is selected
        """
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()

    mutil_del.short_desc = '批量删除'

    def mutil_initial(self, request):
        """
        initial multiple items
        """
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()

    mutil_initial.short_desc = '批量初始化'

    show_actions = False

    combine_filter = []

    def get_com_filter(self):
        result = []
        if self.combine_filter:
            result.extend(self.combine_filter)
        return result

    def gen_com_filter(self):
        # data_list = []
        from django.db.models import ForeignKey, ManyToManyField
        for option in self.combine_filter:
            _fields = self.model_class._meta.get_field(option.field_name)

            if isinstance(_fields, ForeignKey):
                row = FilterRow(option, option.get_queryset(_fields), self.request)
                # data_list.append(row)
            elif isinstance(_fields, ManyToManyField):
                row = FilterRow(option,option.get_queryset(_fields),self.request)
                # data_list.append(row)
            else:
                row = FilterRow(option, option.get_choices(_fields),self.request)
                # data_list.append(row)

            yield row
        # return data_list


    def get_show_actions(self):
        """
        check if it's need to show actions in html
        """
        return self.show_actions


    def search_view(self, request):
        """
        default show all data html
        """
        if request.method == 'POST' and self.get_show_actions():
            func_name_str = request.POST.get('list_actions')
            action_func = getattr(self, func_name_str)
            ret = action_func(request)
            if ret:
                return ret

            pk_list = request.POST.getlist('pk')


        self.request = request
        search_condition = self.get_search_condition()

        combine_condition = {}
        option_list = self.get_com_filter()
        for key in request.GET.keys():
            value_list = request.GET.getlist(key)
            flag = False
            for option in option_list:
                if option.field_name == key:
                    flag = True
                    break
            if flag:
                combine_condition["%s__in"%key] = value_list

        all_objects = self.model_class.objects.filter(search_condition).filter(**combine_condition).distinct()
        show_page = Show(self, request, all_objects)
        add_url = self.get_add_url()
        show_add_btn = self.get_show_add_btn()
        gen_com_filter = self.gen_com_filter()

        context = {
            'show_page': show_page,
            'add_url': add_url,
            'show_add_btn': show_add_btn,
            'gen_com_filter': gen_com_filter,
        }
        return render(request, 'cadmin/show_view.html', context)


    def add_view(self, request, *args, **kwargs):
        # view to deal with add items
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class()
            return render(request, 'cadmin/add_view.html', {'form': form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                list_query_str = request.GET.get("_list_filter")
                list_url = "%s?%s" % (self.get_search_url(), list_query_str)
                return redirect(list_url)
            return render(request, 'cadmin/add_view.html', {'form': form})
            # form = AddModelForm


    def modify_view(self, request, id, *args, **kwargs):
        # edit items in the table
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
        # view for deal with delete items
        self.model_class.objects.filter(pk=id).delete()
        return redirect(self.get_search_url())


    def get_link_tag(self, obj, val):
        """
        Use this to take the params at the end of the url, it's custom key
        """
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
        # get the user's search keyword'
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
        # get urls by url method
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
