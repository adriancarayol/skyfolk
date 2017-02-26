from django.conf.urls import url

from dash.contrib.plugins.rss_feed import views as rss_feed_views

urlpatterns = [
               url(r'^get_feed/(?P<layout_uid>[\w_]+)/(?P<placeholder_uid>[\w_]+)/(?P<plugin_uid>[\w_\-]+)/$',
                   rss_feed_views.get_feed, name='dash.contrib.plugins.rss_feed.get_feed'),
               ]
