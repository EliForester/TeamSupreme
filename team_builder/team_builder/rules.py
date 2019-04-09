import rules

"""
These rules control who is allowed to take actions,
    without object-level permissions
I.e., project owner can edit the project, etc.
"""

# Predicates


@rules.predicate
def is_project_owner(user, project):
    '''

    :param user: User object from template
    :param project: Project object from template
    :return: True if user is project owner, else False
    '''
    return project.owner == user


@rules.predicate
def is_position_owner(user, position):
    '''

    :param user: User object from template
    :param position: Position object from template
    :return: True if user is project owner, else False
    '''
    return position.project.owner == user


@rules.predicate
def is_member_or_pending(user, position):
    '''

    :param user: User object from template
    :param position: Position object from template
    :return: True if the user is retired from a position, else False
    '''
    for participant in position.participant_set.all():
        if participant.user == user:
            if participant.status in ['member', 'pending']:
                return True
    return False


@rules.predicate
def is_participant(user, position):
    '''

    :param user: User object from template
    :param position: Position object from template
    :return: True if the user is already in position.participants, else False
    '''
    return user in position.participants.all()


# Project rules

rules.add_perm('team_builder.edit_project', is_project_owner)
rules.add_perm('team_builder.delete_project', is_project_owner)

# Position rules

allowed_to_join = ~is_position_owner & ~is_member_or_pending
allowed_to_leave = ~is_position_owner & is_member_or_pending

rules.add_perm('team_builder.edit_delete_position', is_position_owner)
rules.add_perm('team_builder.join_position', allowed_to_join)
rules.add_perm('team_builder.leave_position', allowed_to_leave)
