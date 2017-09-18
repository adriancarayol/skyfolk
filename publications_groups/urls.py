from django.conf.urls import url

from . import views

urlpatterns = [
    # Publication for photo
    url(r'^publication_g/$', views.publication_group_view,
        name='new_group_publication'),
    url(r'^publication/group/delete/$', views.delete_publication,
        name='delete_group_publication'),
    url(r'^publication/group/add_like/$', views.AddPublicationLike.as_view(),
        name='add_like_group_publication'),
    url(r'^publication/group/add_hate/$', views.AddPublicationHate.as_view(),
        name='add_hate_group_publication'),
    url(r'^publication/group/edit/$', views.EditGroupPublication.as_view(),
        name='edit_group_publication'),
    url(r'^publication/group/detail/(?P<pk>\d+)/$', views.PublicationGroupDetail.as_view(),
        name='detail_group_publication'),
    url(r'^publication/group/load/replies/$', views.LoadRepliesForPublicationGroup.as_view(),
        name='load_replies_group_publication'),
    url(r'^publication/group/share/$', views.ShareGroupPublication.as_view(),
        name='share_group_publication'),
    url(r'^publication/group/delete/share/$', views.RemoveSharedGroupPublication.as_view(),
        name='delete_share_group_publication'),
    # Theme publications
    url(r'^publication/group/theme/reply/$', views.PublicationThemeView.as_view(),
        name='reply_theme_publication'),

]
