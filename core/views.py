from django.shortcuts import render, redirect

from django.contrib import messages
from core.services.forum import ForumService
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required
def index(request):
    # TODO: Display threads, handle pagination and search.
    #  Later threads, search should be htmx.
    template = "core/index.html"
    context = {
        "threads": ForumService.get_threads(),
        # "tags": Tag.objects.all(),  # TODO: Count by amount of threads.
    }

    if request.method == "GET":
        return render(request, template, context)

    if request.method == "POST":
        return render(request, template, context)


@login_required
def new_thread(request):
    template = "core/new_thread.html"
    context = {}

    if request.method == "GET":
        return render(request, template, context)

    if request.method == "POST":
        # TODO: If thread creation fails, display error message.
        thread = ForumService.create_thread(
            title=request.POST["title"],
            content=request.POST["content"],
            tags=request.POST["tags"].split(","),
            user_id=request.user.id,
        )

        if not thread:
            # TODO: Fix in fe to load content into quill.js if exists.
            context = {
                "title": request.POST["title"],
                "content": request.POST["content"],
                "tags": request.POST["tags"],
            }
            messages.error(request, "Thread title exists!")
            return render(request, template, context)

        messages.success(request, "Thread created!")
        return redirect("thread", thread_pub_id=thread.public_id)


@login_required
def thread(request, thread_pub_id: str):
    # TODO: Thread display + add reply (content, tags?).
    # TODO: Later load each reply via htmx lazy load.
    template = "core/thread.html"
    context = {
        "thread": ForumService.get_thread(thread_pub_id=thread_pub_id),
        "replies": ForumService.get_replies(thread_pub_id=thread_pub_id),
    }

    if request.method == "GET":
        return render(request, template, context)

    if request.method == "POST":

        action = request.POST["action"]

        if action == "create_reply":
            ForumService.add_reply(
                thread_pub_id=thread_pub_id,
                content=request.POST["content"],
                user_id=request.user.id,
            )
            messages.success(request, "Reply added!")
            return redirect("thread", thread_pub_id=thread_pub_id)

        return render(request, template, context)


@login_required
def user_profile(request):
    # TODO: User profile management. Pfp, display name, etc.
    template = "core/user_profile.html"
    context = {}

    if request.method == "GET":
        return render(request, template, context)

    if request.method == "POST":
        return render(request, template, context)


@login_required
@require_http_methods(["GET"])
def delete_reply(request, thread_pub_id: str, reply_pub_id: str):
    ForumService.delete_reply(reply_pub_id=reply_pub_id, user_id=request.user.id)
    messages.success(request, "Reply deleted!")
    return redirect("thread", thread_pub_id=thread_pub_id)

# TODO: Custom decorator that checks for group verified_user, if not, redirects to unverified.html!
#  Ignore if has group mod or is superuser.
