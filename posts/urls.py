from django.urls import path
from posts.views import (
    GroupPostsView,
    follow_index,
    profile_follow,
    profile_unfollow,
    PostCreateView,
    PostDetailView,
    PostUpdateView,
    ProfileView,
    CommentCreateView,
    PostListView,
)

urlpatterns = [
    path("group/<slug:slug>/", GroupPostsView.as_view(), name="group_posts"),
    path("follow/", follow_index, name="follow_index"),
    path("<str:username>/follow/", profile_follow, name="profile_follow"),
    path("<str:username>/unfollow/", profile_unfollow, name="profile_unfollow"),
    path("new/", PostCreateView.as_view(), name="new_post"),
    path("<str:username>/<int:pk>/", PostDetailView.as_view(), name="post_view"),
    path("<str:username>/<int:pk>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("<str:username>/", ProfileView.as_view(), name="profile"),
    path("<username>/<int:post_id>/comment", CommentCreateView.as_view(), name="add_comment"),
    path('', PostListView.as_view(), name="index"),
]
