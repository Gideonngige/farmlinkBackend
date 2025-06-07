from django.contrib import admin
from .models import Farmer, Notification, Question, Reply

# Register your models here.
admin.site.register(Farmer)
admin.site.register(Notification)
admin.site.register(Question)
admin.site.register(Reply)
