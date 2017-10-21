from django.db import models
from django.dispatch import receiver
from my_user.models import User
from api.models import Master
from safedelete.signals import pre_softdelete


# Create your models here.
class Group(Master):
    group_owner = models.ForeignKey(User, related_name='group_owner')
    name = models.CharField(max_length=100, name='name')


class GroupMember(Master):
    user = models.ForeignKey(User, related_name='group_member')
    group = models.ForeignKey(Group, related_name='group')


@receiver(pre_softdelete, sender=Group)
def delete_members_of_group(sender, instance, **kwargs):
    members = GroupMember.objects.filter(group=instance)
    for member in members:
        member.delete()
