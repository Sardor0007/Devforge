import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.messaging.routing
import apps.notifications.routing
import apps.workspace.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devforge.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.messaging.routing.websocket_urlpatterns +
            apps.notifications.routing.websocket_urlpatterns +
            apps.workspace.routing.websocket_urlpatterns
        )
    ),
})
