from datetime import datetime
from rest_framework import serializers
from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('text', 'author', 'pub_date')
        model = Post

    text = serializers.TextField()
    author = serializers.CharField(max_length=200)
    pub_date = serializers.DateTimeField()


post = Post(author="Лев Толстой", text="17 Марта. Написалъ около листа Юности хорошо - И легъ поздно.")
serializer = PostSerializer(post)
