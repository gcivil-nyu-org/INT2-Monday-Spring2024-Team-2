from django.shortcuts import render, get_object_or_404, redirect
from TutorRegister.models import ChatSession, Message, ProfileT, ProfileS
from django.contrib.auth.models import User
from django.db.models import Q


def chat_view(request, other_user_id):
    user = request.user
    profiles = []
    other_user = get_object_or_404(User, id=other_user_id)
    ChatSession.objects.get_or_create(
        tutor=(
            request.user if request.user.usertype.user_type == "tutor" else other_user
        ),
        student=(
            request.user if request.user.usertype.user_type == "student" else other_user
        ),
    )
    if user.usertype.user_type == "tutor":
        tutor = get_object_or_404(ProfileT, user=request.user)
        student = get_object_or_404(ProfileS, user=other_user)
        chats = ChatSession.objects.filter(tutor_id=request.user.id)
        student_ids = chats.values_list("student_id", flat=True).distinct()
        profiles = ProfileS.objects.filter(user_id__in=student_ids)
    elif user.usertype.user_type == "student":
        tutor = get_object_or_404(ProfileT, user=other_user)
        student = get_object_or_404(ProfileS, user=request.user)
        chats = ChatSession.objects.filter(student_id=request.user.id)
        tutor_ids = chats.values_list("tutor_id", flat=True).distinct()
        profiles = ProfileT.objects.filter(user_id__in=tutor_ids)

    print(student.id)
    print(tutor.id)
    chat_session = ChatSession.objects.filter(
        (Q(tutor=user) & Q(student=other_user))
        | (Q(tutor=other_user) & Q(student=user))
    ).first()

    messages = []
    if chat_session:
        messages = Message.objects.filter(chat_session=chat_session).order_by(
            "timestamp"
        )

    context = {
        "baseTemplate": (
            "Dashboard/base_student.html"
            if request.user.usertype.user_type == "student"
            else "Dashboard/base_tutor.html"
        ),
        "student": student,
        "tutor": tutor,
        "other_user_id": other_user_id,
        "messages": messages,
        "profiles": profiles,
    }
    return render(request, "chat/chat.html", context)


def display_chats(request):
    chats = (
        ChatSession.objects.filter(student=request.user)
        .union(ChatSession.objects.filter(tutor=request.user))
        .order_by("created_at")
    )

    if chats.exists():
        first_chat = chats.first()
        return redirect(
            "Chat:chat_view",
            other_user_id=(
                first_chat.student.id
                if request.user != first_chat.student
                else first_chat.tutor.id
            ),
        )
    else:
        # Render a template with a message that no chats are present
        context = {
            "baseTemplate": (
                "Dashboard/base_student.html"
                if request.user.usertype.user_type == "student"
                else "Dashboard/base_tutor.html"
            ),
        }
        return render(request, "chat/no_chats.html", context=context)


# sudo service redis-server stop
