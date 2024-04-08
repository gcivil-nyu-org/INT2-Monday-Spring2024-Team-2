from django.shortcuts import render, get_object_or_404, redirect
from .forms import CreatePostForm, CreateReplyForm
from django.db import IntegrityError, DatabaseError
from django.core.paginator import Paginator
from django.contrib import messages
from TutorRegister.models import Post, Reply, ProfileT, ProfileS


def view_all_posts(request):
    userType = request.user.usertype.user_type
    
    posts = Post.objects.all().order_by("-post_date")
    paginator = Paginator(posts, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    replies = Reply.objects.all().order_by("-reply_date")
    replied_users = set(reply.user for reply in replies)

    users = set(post.user for post in posts)

    user_profiles = []
    for user in users:
        # Check if the user is a tutor
        if hasattr(user, "profilet"):
            profile = ProfileT.objects.get(user=user)
        # If not a tutor, assume it's a student
        else:
            profile = ProfileS.objects.get(user=user)
        user_profiles.append(profile)

    reply_count = {}

    for p in posts:
        count = replies.filter(post=p).count()
        reply_count[p] = count

    replied_profile = []
    for user in replied_users:
        # Check if the user is a tutor
        if hasattr(user, "profilet"):
            profile = ProfileT.objects.get(user=user)
        # If not a tutor, assume it's a student
        else:
            profile = ProfileS.objects.get(user=user)
        replied_profile.append(profile)

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
        "profiles": user_profiles,
        "replies": replies,
        "reply_count": reply_count,
        "replied_profiles": replied_profile,
        "form": form,
    }
    # return render all posts
    return render(request, "posts.html", context)


def view_post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    # replies = Reply.objects.filter(post=post).order_by("reply_date")

    if request.method == "POST":
        form = CreateReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.save()

            return redirect("Community:all_posts")
            # return redirect to post detail page
        else:
            form = CreateReplyForm()
    return render(request, "posts.html", {"post": post, "r_form": form})
    # render post detail page


def create_post(request):
    userType = request.user.usertype.user_type
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                return redirect("Community:all_posts")
                # return redirect to post page
            except (IntegrityError, DatabaseError) as e:
                print(e)
                # return render to create post page with error message
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
    # return render to create post page
