from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.dispatch import receiver
from notifications.signals import notify

from .models import Participant


@receiver(pre_save, sender=Participant)
def participant_notifier(sender, **kwargs):
    """
    Checks presave Participant object.
    If new: (no record -> new record)
        send notice to project owner that someone wants to join
    If updated from pending->member:
        send notice to participant that appication was approved
    If updated from pending->rejected:
        send notice to participant that appication was rejected
    If updated from anything->left:
        send notice to project owner that someone left
    """
    participant = kwargs['instance']
    try:
        # If existing model was approved then send to applicant
        old_participant = Participant.objects.get(pk=participant.id)
        verb = ''
        if old_participant.status == 'pending' and \
                participant.status == 'member':
            verb = 'Your application for "{}" in "{}" was approved'
        elif old_participant.status == 'pending' and \
                participant.status == 'rejected':
            verb = 'Your application for "{}" in "{}" was rejected'
        elif old_participant.status == 'member' and \
                participant.status == 'retired':
            verb = 'You have been retired from "{}" in "{}"'
        if verb:
            notify.send(participant.position.project.owner,
                        recipient=participant.user,
                        verb=verb.format(
                            participant.position.position_name,
                            participant.position.project.name),
                        action_object=participant.position)
        if participant.status == 'left':
            notify.send(participant.user,
                        recipient=participant.position.project.owner,
                        verb='{} has left "{}" position "{}"'
                        .format(
                            participant.user,
                            participant.position.project.name,
                            participant.position.position_name),
                        action_object=participant.position)
    except ObjectDoesNotExist:
        # If new participant then send to project owner
        notify.send(participant.user,
                    recipient=participant.position.project.owner,
                    verb='{} would like to join "{}" as "{}"'.format(
                        participant.user,
                        participant.position.project.name,
                        participant.position.position_name),
                    action_object=participant.position)
