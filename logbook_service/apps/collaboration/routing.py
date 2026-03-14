from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/entries/(?P<entry_id>[0-9a-f-]+)/$",
        consumers.CollaborationConsumer.as_asgi(),
    ),
]
