#!/usr/bin/env python
#coding:utf-8
#Created by Andy @ 2018/3/21



from django.conf.urls import url
from crm import views
urlpatterns = [
    url(r'^index/', views.index),
]
