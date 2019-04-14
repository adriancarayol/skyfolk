from django.urls import path

from about.views import EntryListView, PublicationBlogDetailView

app_name = "about"

urlpatterns = [
    path("blog/", EntryListView.as_view(), name="blog"),
    path(
        "blog/publication/<int:pk>/",
        PublicationBlogDetailView.as_view(),
        name="publication-blog",
    ),
]
