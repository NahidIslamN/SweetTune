
import os

# Ensure settings module is set before importing Django apps or ASGI components
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SweetTune.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
# create the Django ASGI application first (this will populate apps)
django_asgi_app = get_asgi_application()

# Import app routing and middleware after Django apps are loaded
from chats.routing import websocket_urlpatterns
from .custom_auth import CustomAuthMiddleware

application = ProtocolTypeRouter(
    {
        'http': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            CustomAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            )
        ),
    }
)



