from django.shortcuts import render, get_object_or_404, redirect
from .forms import CreatePostForm, CreateReplyForm
from django.db import IntegrityError, DatabaseError
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count, Prefetch
from TutorRegister.models import Post, Reply, ProfileT, ProfileS
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
                queryset=Reply.objects.order_by("reply_date").select_related(
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

    # Prepare processed topics for display in the dropdown menu
    processed_topics = [{topic: get_display_topic(topic)} for topic in all_topics]

    topic = request.GET.get("topic")
    print(topic)

    if topic:
        if topic not in all_topics:
            for item in processed_topics:
                if topic in item.values():
                    topic = list(item.keys())[0]
                    break
        print(topic)
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
        # return redirect to post detail page
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
    # render post detail page


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


def get_display_topic(topic):
    if topic == "{}":
        return "None"
    else:
        return get_display_expertise(topic)
