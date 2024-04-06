from django.shortcuts import render, get_object_or_404
from .forms import CreatePostForm, CreateReplyForm
from django.db import IntegrityError, DatabaseError
from django.core.paginator import Paginator
from TutorRegister.models import Post, Reply


def view_all_posts(request):
    posts = Post.object.all().order_by("-post_date")
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # return render all posts


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
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.user = request.user
                post.save()

                # return redirect to post page
            except (IntegrityError, DatabaseError) as e:
                print(e)
                # return render to create post page with error message

    else:
        form = CreatePostForm()

    # return render to create post page
