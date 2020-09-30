from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User, Comment
from .helper import get_user_profile, check_following

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
)

class PostListView(ListView):
    """ Gets a selection of 10 entries per page."""
    model = Post
    template_name = "index.html"
    paginate_by = 3
    context_object_name = 'posts'


class GroupPostsView(ListView):
    """
    Сommunity page with posts
    """
    model = Group
    paginate_by = 2
    template_name = "group.html"
    queryset = Post.objects.all()


class PostCreateView(LoginRequiredMixin , CreateView):
    """
    Adds a new publication.
    After validating the form and creating a new post,
    the author is redirected to the main page.
    """
    model = Post
    template_name = "posts/new_post.html"
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("index")


class ProfileView(ListView):
    """
    Adds a profile page with posts
    return: page "profile.html"
    """
    model = Post
    paginate_by = 5
    template_name = "profile.html"

    def get_queryset(self):
        # author = get_object_or_404(User, username=self.request.user)
        author = get_user_profile(self.kwargs['username'])
        self.kwargs['author'] = author
        return (
            author.author_posts.select_related('author', 'group')
                .annotate(comment_count=Count('comments'))
                .all()
        )

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['author'] = self.kwargs['author']
        context['following'] = check_following(self.request.user, context['author'])
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    """
    Creates a Page for viewing a separate post
    return: page "post_view.html"
    """
    model = Post
    template_name = "post_view.html"
    form_class = CommentForm
    extra_context = {
        'form': CommentForm(),
    }

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['username'] = get_object_or_404(User, username=self.request.user)
        context['author'] = context['username']
        context['count_posts'] = context['author'].author_posts.count()
        return context

    @property
    def success_url(self):
        return reverse('post_view', kwargs={'username': self.request.user,
                                            'pk': self.object.pk})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """
       Creating a page for editing an existing post
       return: the page with the changed post.
    """
    model = Post
    form_class = PostForm
    template_name = "posts/new_post.html"

    # pk_url_kwarg = "post_id"

    def get_context_data(self, **kwargs):
        context = super(PostUpdateView, self).get_context_data(**kwargs)
        context['username'] = get_object_or_404(User, username=self.request.user)
        context['is_edit'] = True
        return context

    @property
    def success_url(self):
        return reverse('post_view', kwargs={'username': self.request.user,
                                            'pk': self.object.pk})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    Creating a comment for editing an existing post
    return: the page with comment or the page for viewing the post.
    """
    model = Comment
    form_class = CommentForm
    template_name = "includes/comments.html"
    extra_context = {
        'comments_form': CommentForm()
    }

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.post = Post.objects.get(pk=self.kwargs.get("post_id"))
        self.object.save()
        return super().form_valid(form)

    @property
    def success_url(self):
        return reverse('post_view', kwargs={'username': self.request.user,
                                            'pk': self.object.post.pk})


@login_required
def follow_index(request):
    """
    Displays posts of authors that the current user is subscribed to.
    :param request:
    :return: the page with posts of authors that the current user is subscribed to.
    """
    author = get_object_or_404(User, username=request.user)
    post_list = Post.objects.filter(author__following__user=request.user)
    count_posts = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "follow.html",
                  {"author": author,
                   "count_posts": count_posts,
                   "page": page,
                   "paginator": paginator,
                   })


@login_required
def profile_follow(request, username):
    """
    Subscribes to an interesting author.
    """
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if not request.user == author and follow is False:
        Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    """
    Unsubscribes from the author.
    """
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):  # noqa
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


