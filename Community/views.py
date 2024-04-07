from django.shortcuts import render, get_object_or_404, redirect
from .forms import CreatePostForm, CreateReplyForm
from django.db import IntegrityError, DatabaseError
from django.core.paginator import Paginator
from django.contrib import messages
from TutorRegister.models import Post, Reply


def view_all_posts(request):
    posts = Post.objects.all().order_by("-post_date")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    users = set(post.user for post in posts)

    context = {
        "posts": posts,
        "users": users,
    }
    # return render all posts
    return render(request, "posts.html", context)

def view_post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    replies = Reply.objects.filter(post=post).order_by("reply_date")

    if request.method == "POST":
        form = CreateReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.save()
          
            # return redirect to post detail page
        else:
            form = CreateReplyForm()

    # render post detail page


def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                messages.success(request, 'Post created successfully!')
                return redirect("Community:all_posts")
                # return redirect to post page
            except (IntegrityError, DatabaseError) as e:
                messages.error(request, f'An error occurred: {e}')
                # return render to create post page with error message
    else:
        form = CreatePostForm()

    return render(request, "create_post.html", {"form": form})
    # return render to create post page
