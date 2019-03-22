from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Participant
from notifications.signals import notify


@receiver(pre_save, sender=Participant)
def participant_notifier(sender, **kwargs):
    participant = kwargs['instance']
    try:
        # If existing model was approved then send to applicant
        old_participant = Participant.objects.get(pk=participant.id)
        verb = ''
        if old_participant.status == 'pending' and participant.status == 'member':
            verb = ' was approved for {} in {} {}'
        elif old_participant.status == 'pending' and participant.status == 'rejected':
            verb = ' was rejected for {} in {} {}'
        notify.send(participant.position.project.owner,
                    recipient=participant.user,
                    verb=verb.format(
                        participant.position.position_name,
                        participant.position.project.name,
                        participant.id),
                    action_object=participant.position)
    except:
        # If new participant then send to project owner
        notify.send(participant.user,
                    recipient=participant.position.project.owner,
                    verb=' would like to join {} as {}'.format(
                        participant.position.project.name,
                        participant.position.position_name),
                    action_object=participant.position)
