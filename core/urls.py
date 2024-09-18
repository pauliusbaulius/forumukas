from django.urls import path

from core.views import index,  thread, new_thread, user_profile, delete_reply

urlpatterns = [
    path("", index, name="index"),
    path("thread/new/", new_thread, name="new-thread"),
    path("thread/<str:thread_pub_id>/", thread, name="thread"),
    path("user/profile/", user_profile, name="user-profile"),
    path("reply/delete/<str:thread_pub_id>/<str:reply_pub_id>/", delete_reply, name="delete-reply"),
]
