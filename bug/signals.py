from django.dispatch import receiver
from django.db.models.signals import (post_save,)
from bug.models import Bug, BugWorkqueueStatus

@receiver(post_save, sender=Bug)
def create_new_bugworkqueuestatus(sender, instance, created, **kwargs):
    if created:
        BugWorkqueueStatus.objects.create(
                bug_wq                          = instance,
                workqueue_status                = 'New', 
                workqueue_comment               = 'New Bug',    
            )