from django.apps import AppConfig


class TeamBuilderConfig(AppConfig):
    name = 'team_builder'

    def ready(self):
        import team_builder.signals
