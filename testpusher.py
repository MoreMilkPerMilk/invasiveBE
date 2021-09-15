
from config.settings import settings
import pusher

pusher_client = pusher.Pusher(
  app_id=settings.pusher['app_id'],
  key=settings.pusher['key'],
  secret=settings.pusher['secret'],
  cluster=settings.pusher['cluster'],
  ssl=True
)

pusher_client.trigger('my-channel', 'my-event', {'message': 'hello world'})

