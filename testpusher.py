from pusher_push_notifications import PushNotifications
from config.settings import settings

beams_client = PushNotifications(
    instance_id=settings.pusher_instance_id,
    secret_key=settings.pusher_key
)