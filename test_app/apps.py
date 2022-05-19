from django.apps import AppConfig


class TestAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'test_app'

    def ready(self):
        import test_app.signals

        # @todo uncomment this for weekly update of the topics
        from topics_updater import update
        update.start()

