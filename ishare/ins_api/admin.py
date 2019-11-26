from django.contrib import admin
from .models import ApiApplicationer,ApiList
from django.core.mail import EmailMessage  
from django.contrib.auth.hashers import make_password
import random
import string
import rsa 
import os

seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def sendEmail(modeladmin, request, queryset):
	sendEmail.short_description = "发送邮件"
	for apper in queryset:
		sa = []
		for i in range(16):
			sa.append(random.choice(seed))

		appID = apper.email[:4] + "_"
		appID +=  ''.join(sa)
		sa = []
		for i in range(7):
			sa.append(random.choice(seed))

		appKey = ''.join(sa)
		appKey = make_password(appKey)[20:80]
		fd = open('Ins_API.txt', 'w')
		fd.write("AppID: " + appID +'\n')
		fd.write("AppKey: " + appKey+ '\n')
		fd.close
		ApiList.objects.create(appId=appID,appKey=appKey)
		email = EmailMessage("接口申请成功","请注意查收附件。", "alex_noreply@163.com", [apper.email])
		email.content_subtype = "html"
		fd = open('Ins_API.txt', 'r')
		email.attach('Ins_API.txt', fd.read(), 'text/plain')
		email.send()
		os.remove('Ins_API.txt')




@admin.register(ApiApplicationer)
class ApiApplicationerAdmin(admin.ModelAdmin):
	list_display = ('email','name')
	search_fields = ('email','name')
	actions = [sendEmail]
		
# Register your models here.
