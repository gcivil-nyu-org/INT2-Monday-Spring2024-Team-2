from django.shortcuts import render, get_object_or_404, redirect
from .forms import CreatePostForm, CreateReplyForm
from django.db import IntegrityError, DatabaseError
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count, Prefetch
from TutorRegister.models import Post, Reply, ProfileT, ProfileS


def view_all_posts(request):
    userType = request.user.usertype.user_type

    posts = (
        Post.objects.select_related("user__usertype")
        .prefetch_related(
            Prefetch(
                "post_replies",
                queryset=Reply.objects.order_by("reply_date").select_related(
                    "user__usertype"
                ),
                to_attr="ordered_replies",
            )
        )
        .annotate(reply_count=Count("post_replies"))
        .order_by("-post_date")
    )

    paginator = Paginator(posts, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        form = CreateReplyForm(request.POST)
        if form.is_valid():
            post_id = request.POST.get("post_id")
            post = get_object_or_404(Post, pk=post_id)
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.save()
            return redirect("Community:all_posts")
    else:
        form = CreateReplyForm()

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "posts": page_obj,
        "form": form,
    }
    # return render all posts
    return render(request, "posts.html", context)


# def view_post_detail(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     # replies = Reply.objects.filter(post=post).order_by("reply_date")

#     if request.method == "POST":
#         form = CreateReplyForm(request.POST)
#         if form.is_valid():
#             reply = form.save(commit=False)
#             reply.user = request.user
#             reply.post = post
#             reply.save()

#             return redirect("Community:all_posts")
#             # return redirect to post detail page
#         else:
#             form = CreateReplyForm()
#     return render(request, "posts.html", {"post": post, "r_form": form})
#     # render post detail page


def create_post(request):
    userType = request.user.usertype.user_type
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("Community:all_posts")
    else:
        form = CreatePostForm()

    context = {
        "form": form,
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
    }

    return render(request, "create_post.html", context)
