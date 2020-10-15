from django.contrib import admin

# Register your models here.
from .models import Bug, BugWorkqueueStatusTypes, BugComment, BugWorkqueueStatus, BugPriorityTypes, BugCategoryTypes
admin.site.register(Bug)
admin.site.register(BugWorkqueueStatusTypes)
admin.site.register(BugComment)
admin.site.register(BugWorkqueueStatus)
admin.site.register(BugPriorityTypes)
admin.site.register(BugCategoryTypes)