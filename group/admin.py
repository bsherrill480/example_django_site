from django.contrib import admin
from .models import GroupMember, Group

# Register your models here.
admin.site.register(Group)
admin.site.register(GroupMember)
