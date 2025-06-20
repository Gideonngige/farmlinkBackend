from django.contrib import admin
from .models import Farmer, Notification, Question, Reply, Product, ProductOrder

# Register your models here.
admin.site.register(Farmer)
admin.site.register(Notification)
admin.site.register(Question)
admin.site.register(Reply)
admin.site.register(Product)
admin.site.register(ProductOrder)
