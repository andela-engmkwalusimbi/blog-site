from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Count
from taggit.models import Tag
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


# class based view for posts using a generic VIew
# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


class PostListView(View):
    template_name = 'blog/post/list.html'

    def get(self, request, *args, **kwargs):
        posts_list = Post.published.all()
        tag = None


# Create your views here.
def post_list(request, tag_slug=None):
    posts_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_list = posts_list.filter(tags__in=[tag])
    paginator = Paginator(posts_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post, slug=post, status='published',
        publish__year=year, publish__month=month, publish__day=day )
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    comment_form = CommentForm()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            comment_form = CommentForm()
    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    payload = {
        'post': post, 'comments': comments,
        'comment_form': comment_form, 'similar_posts': similar_posts}
    return render(request, 'blog/post/detail.html', payload)

def post_share(request, post_id):
    form = EmailPostForm()
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{name} ({email}) recommends you reading "{title}"'.format(
                name=cd['name'], email=cd['email'], title=post.title)
            message = 'Read "{title}" at {url}\n\n{name}\'s comments: {comments}'.format(
                title=post.title, url=post_url, name=cd['name'], comments=cd['comments'])
            send_mail(subject, message, 'mahad.walusimbi@andela.com', [cd['to']])
            sent = True
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'cd': cd, 'sent': sent})