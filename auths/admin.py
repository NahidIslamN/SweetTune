from django.contrib import admin
from .models import CustomUser, OtpTable
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(OtpTable)



from django.contrib import admin

admin.site.site_header = "Sweet Tune Admin"
admin.site.site_title = "Sweet Tune Portal"
admin.site.index_title = "Welcome to Sweet Tune Dashboard"