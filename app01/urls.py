#!/usr/bin/env python
#coding:utf-8
#Created by Andy @ 2018/3/15



from django.conf.urls import url
from app01 import views
urlpatterns = [
    url(r'^index/', views.index),
]
