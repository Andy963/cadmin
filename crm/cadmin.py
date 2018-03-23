#!/usr/bin/env python
# coding:utf-8
# Created by Andy @ 2018/3/21



from cadmin.service import cadmin
from crm.models import *
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import redirect, HttpResponse


class UserInfoConfig(cadmin.CadminConfig):
    # TODO: when depart is empty the other field wil not show in html
    list_display = ['name', 'username', 'email', 'depart']
    search_fields = ["name", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True

    combine_filter = [
        cadmin.FilterOption('depart', text_func_name=lambda x: str(x), val_func_name=lambda x: x.code, ),
    ]


class DepartmentConfig(cadmin.CadminConfig):
    list_display = ['title', 'code']
    search_fields = ["code", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True
    edit_link = ['title', ]


class CourseConfig(cadmin.CadminConfig):
    list_display = ['name', ]
    search_fields = ["name", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True


class SchoolConfig(cadmin.CadminConfig):
    list_display = ['title', ]
    search_fields = ["title", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True


class ConsultRecordConfig(cadmin.CadminConfig):
    def show_view(self, request, *args, **kwargs):
        customer = request.GET.get('customer')
        current_login_user_id = 1
        ct = models.Customer.objects.filter(consultant=current_login_user_id, id=customer).count()
        if not ct:
            return HttpResponse('Dont do that!')
        return super(ConsultRecordConfig, self).show_search(request, *args, **kwargs)
    list_display = ['customer', ]
    search_fields = ["consultant", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True

    combine_filter = [
        cadmin.FilterOption('customer'),
        cadmin.FilterOption('consultant'),
    ]
    show_combine_filter = False


class PaymentRecordCondfig(cadmin.CadminConfig):
    list_display = ['customer', ]
    search_fields = ["class_list", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True

    combine_filter = [
        cadmin.FilterOption('customer', True),
        cadmin.FilterOption('class_list', True),
        cadmin.FilterOption('pay_type', is_choice=True),
        cadmin.FilterOption('consultant', True),
    ]


class StudentConfig(cadmin.CadminConfig):
    list_display = ['username', 'class_list', ]
    search_fields = ["username", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True


class CourseRecordConfig(cadmin.CadminConfig):
    list_display = ['teacher', 'course_title']
    search_fields = ["teacher", "course_title", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True


class StudyRecordConfig(cadmin.CadminConfig):
    list_display = ['course_record', 'student', 'score']
    search_fields = ["student", ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True


class CustomerDistrbuteConfig(cadmin.CadminConfig):
    list_display = ['customer', 'consultant', ]
    search_fields = ["customer", 'status', ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True


class ClassListConfig(cadmin.CadminConfig):
    def course_semester(self, obj=None, is_header=False):
        if is_header:
            return 'class'
        return "%s(%s期)" % (obj.course.name, obj.semester,)

    def student_num(self, obj=None, is_header=False):
        if is_header:
            return 'Student Number'
        return 666  # TODO: get the class students num, M2M

    list_display = ['school', 'course', course_semester, 'start_date']
    search_fields = ["school", "course", 'price', ]
    actions = ['multi_del', 'multi_init']
    show_add_btn = True  # add new userinfo button
    show_actions = True


class CustomerConfig(cadmin.CadminConfig):
    def display_gender(self, obj=None, is_header=False):
        if is_header:
            return 'gender'
        return obj.get_gender_display()

    def display_education(self, obj=None, is_header=False):
        if is_header:
            return 'education'
        return obj.get_education_display()

    def display_course(self, obj=None, is_header=False):
        if is_header:
            return 'consult class'

        course_list = obj.course.all()
        html = []
        for item in course_list:
            temp = "<a style='display:inline-blokc;padding:3px;border:1px solid blue;margin:2px;' href='%s/%s/cc/'>%s</a>" % (
                obj.pk, item.pk, item.name)
            html.append(temp)
        return mark_safe("".join(html))

    def cancel_course(self, request, customer_id, course_id):
        customer_obj = self.model_class.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)

        return redirect(self.get_search_url())

    def record(self, obj=None, is_header=False):
        if is_header:
            return 'Record'
        return mark_safe("<a href=#id=%s>check record</a>"%(obj.pk))

    def extra_url(self):
        app_label, app_model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        patterns = [
            url(r'^(\d+)/(\d+)/cc/$',self.wrap(self.cancel_course),name="%s_%s_cc"%(app_label, app_model_name))
        ]
        return patterns

    list_display = ['qq', 'name', display_gender, display_education, 'major',record, 'company', 'salary', display_course]


cadmin.site.register(Department, DepartmentConfig)
cadmin.site.register(UserInfo, UserInfoConfig)
cadmin.site.register(Course, CourseConfig)
cadmin.site.register(School, SchoolConfig)
cadmin.site.register(ClassList, ClassListConfig)
cadmin.site.register(Customer, CustomerConfig)
cadmin.site.register(ConsultRecord, ConsultRecordConfig)
cadmin.site.register(PaymentRecord, PaymentRecordCondfig)
cadmin.site.register(Student, StudentConfig)
cadmin.site.register(CourseRecord, CourseConfig)
cadmin.site.register(StudyRecord, StudentConfig)
cadmin.site.register(CustomerDistrbute, CustomerDistrbuteConfig)
