from django.contrib import admin
from api.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'finished', 'user_id')


admin.site.register(Task, TaskAdmin)
