from django.contrib import admin
from .models import CustomUser, Offer, Notification

admin.site.register(CustomUser)
admin.site.register(Offer)
admin.site.register(Notification)

