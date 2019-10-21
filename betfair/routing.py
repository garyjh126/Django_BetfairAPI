from django.urls import path, re_path
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from login.consumers import NewsCollectorAsyncConsumer

application = ProtocolTypeRouter({
    "http": URLRouter([
        # Our async news fetcher
        path("collector/collect_news_async/", NewsCollectorAsyncConsumer),

        # AsgiHandler is "the rest of Django" - send things here to have Django
        # views handle them.
        re_path("^", AsgiHandler),
    ]),
})