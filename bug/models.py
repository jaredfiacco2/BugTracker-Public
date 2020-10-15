from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Bug(models.Model):
    ###########################Form Related Columns#######################
    title                           = models.CharField(max_length = 100, blank=False)
    description                     = models.CharField(max_length = 4000, blank=False)
    priority                        = models.CharField(max_length=255, blank=False)
    category                        = models.CharField(max_length=255, blank=False)
    submission_dts                  = models.DateTimeField(default=timezone.now)
    requestor                       = models.CharField(max_length=255, blank=False)
    requestor_email                 = models.EmailField(max_length=255, blank=False)
        
    def _str_(self):
        return self.title
    
    def set_username(sender, instance, **kwargs):
        if not instance.username:
            instance.username = instance.first_name
    models.signals.pre_save.connect(set_username, sender=User)

class  BugWorkqueueStatus(models.Model):
    ###########################Workqueue Related Columns#########################
    bug_wq                          = models.ForeignKey('bug.Bug', on_delete=models.CASCADE, related_name='statuses')
    workqueue_status                = models.CharField(max_length=255, blank=False)
    workqueue_comment               = models.CharField(max_length=512, blank=False)
    workqueue_lastupdatedts         = models.DateTimeField(default=timezone.now)
    workqueue_employee              = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    

class  BugComment(models.Model):
    ###########################Workqueue Related Columns#########################
    bug_com                         = models.ForeignKey('bug.Bug', on_delete=models.CASCADE, related_name='comments')
    commentor                       = models.CharField(max_length=255, blank=False)
    comment                         = models.CharField(max_length=512, blank=False)
    comment_dts                     = models.DateTimeField(default=timezone.now)


class BugWorkqueueStatusTypes(models.Model):
    ###########################Form Related Columns#######################
    statustype                  = models.CharField(max_length=255, blank=False)
    def __str__(self):
        return self.statustype

class BugPriorityTypes(models.Model):
    ###########################Form Related Columns#######################
    priority                  = models.CharField(max_length=255, blank=False)
    def __str__(self):
        return self.priority

class BugCategoryTypes(models.Model):
    ###########################Form Related Columns#######################
    category                  = models.CharField(max_length=255, blank=False)
    def __str__(self):
        return self.category
