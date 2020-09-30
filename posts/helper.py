from django.db.models import Count
from django.shortcuts import get_object_or_404

from posts.models import User, Follow


def get_user_profile(username):
    return get_object_or_404(
        User.objects.annotate(
            count_of_posts=Count('author_posts', distinct=True),
            count_of_following=Count('following', distinct=True),
            count_of_follower=Count('follower', distinct=True)
        ),
        username=username)

def check_following(user, author):
    if not user.is_authenticated:
        return False
    return Follow.objects.filter(user=user.id, author=author).exists()
