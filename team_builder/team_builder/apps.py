from django.apps import AppConfig


class TeamBuilderConfig(AppConfig):
    name = 'team_builder'

    def ready(self):
        '''
        Imports the signals required to send notifications using signals.py
        Use this to avoid recursive imports
        '''
        import team_builder.signals
