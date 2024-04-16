from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import CreatePostForm, CreateReplyForm
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from TutorRegister.models import Post, Reply, Vote
from TutorFilter.views import get_display_expertise
from TutorRegister.presets import EXPERTISE_CHOICES


def view_all_posts(request):
    userType = request.user.usertype.user_type
    labels = ["resource", "question"]

    posts = (
        Post.objects.select_related("user__usertype")
        .prefetch_related(
            Prefetch(
                "post_replies",
                queryset=Reply.objects.order_by("-reply_date").select_related(
                    "user__usertype"
                ),
                to_attr="ordered_replies",
            )
        )
        .annotate(reply_count=Count("post_replies"))
        .order_by("-post_date")
    )

    label = request.GET.get("label")

    if label:
        posts = posts.filter(label=label)

    all_topics = [item[0] for item in EXPERTISE_CHOICES]
    all_topics.append("{}")

    # Prepare processed topics for display in the dropdown menu
    processed_topics = [{topic: get_display_topic(topic)} for topic in all_topics]

    topic = request.GET.get("topic")

    if topic:
        if topic not in all_topics:
            for item in processed_topics:
                if topic in item.values():
                    topic = list(item.keys())[0]
                    break
        posts = posts.filter(topics=topic)

    for post in posts:
        post.topics = get_display_topic(post.topics)

    paginator = Paginator(posts, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "posts": page_obj,
        "labels": labels,
        "topics": processed_topics,
    }
    # return render all posts
    return render(request, "posts.html", context)


def view_post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    replies = Reply.objects.filter(post=post).order_by("-reply_date")
    userType = request.user.usertype.user_type
    num_r = replies.count()

    post.topics = get_display_topic(post.topics)

    paginator = Paginator(replies, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        form = CreateReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.save()

        return redirect("Community:post_detail", post_id=post.id)
    else:
        form = CreateReplyForm()

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "replies": page_obj,
        "r_form": form,
        "post": post,
        "num_r": num_r,
    }

    return render(request, "post_detail.html", context)


@login_required
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
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "form": form,
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
    }

    return render(request, "create_post.html", context)


@login_required
def edit(request, post_id):
    userType = request.user.usertype.user_type
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.user:
        return redirect("Community:post_detail", post_id=post_id)

    if request.method == "POST":
        form = CreatePostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("Community:post_detail", post_id=post_id)
    else:
        form = CreatePostForm(instance=post)

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if userType == "student"
            else "Dashboard/base_tutor.html"
        ),
        "form": form,
    }

    return render(request, "edit_post.html", context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check if the current user is the author of the post
    if request.user == post.user:
        # If the request method is POST, delete the post
        if request.method == "POST":
            post.delete()
            return JsonResponse({"success": True})
        else:
            # If the request method is not POST, return a JSON response indicating authorization
            return JsonResponse({"authorized": True})
    else:
        # If the current user is not the author, 
        # return a JSON response indicating lack of authorization
        return JsonResponse({"authorized": False}, status=403)


def vote(request, post_id, vote_type):
    post = get_object_or_404(Post, pk=post_id)
    user_react, created = Vote.objects.get_or_create(user=request.user, post=post)

    if vote_type == "upvote":
        new_value = 1 if user_react.value != 1 else 0
    elif vote_type == "downvote":
        new_value = -1 if user_react.value != -1 else 0

    user_react.value = new_value
    user_react.save()

    rating = post.get_rating()

    return JsonResponse({"rating": rating})


def get_display_topic(topic):
    if topic == "{}":
        return "Other"
    else:
        return get_display_expertise(topic)
