from core.models import Reply, Thread, ThreadSchema
from django.core.paginator import Paginator


class ForumService:
    """Wrapper for all forum related operations to have skinny views."""

    @classmethod
    def thread_exists(cls, thread_pub_id: str) -> bool:
        return Thread.objects.filter(public_id=thread_pub_id).exists()

    @classmethod
    def reply_exists(cls, reply_pub_id: str) -> bool:
        return Reply.objects.filter(public_id=reply_pub_id).exists()

    @classmethod
    def can_update_delete_thread(cls, user_id: int, thread_pub_id: str) -> bool:
        return True

    @classmethod
    def can_update_delete_reply(cls, user_id: int, reply_pub_id: str) -> bool:
        return True

    @classmethod
    def create_thread(cls, title: str, content: str, tags: list[str], user_id: int) -> Thread | None:
        if Thread.objects.filter(title=title).exists():
            return None

        thread = Thread.objects.create(
            title=title,
            created_by_id=user_id,
        )

        Reply.objects.create(
            content=content,
            thread_id=thread.id,
            created_by_id=user_id,
        )

        # TODO: Handle tags!

        # TODO: Index in search.
        return thread

    @classmethod
    def update_thread(
        cls,
        thread_pub_id: str,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> Thread | None:
        if not cls.can_update_delete_thread(user_id=1, thread_pub_id=thread_pub_id):
            return None

        if not cls.thread_exists(thread_pub_id=thread_pub_id):
            return None

        # TODO: Update in db and index.
        return

    @classmethod
    def get_thread(cls, thread_pub_id: str) -> ThreadSchema:
        # TODO: Handle 404.
        q = Thread.objects.get(public_id=thread_pub_id)
        return q.as_schema()

    @classmethod
    def get_threads(cls, limit: int = 25, page: int = 1) -> list[ThreadSchema]:
        # TODO: Should return from search engine sorted by score/date.
        return Thread.objects.all()

    @classmethod
    def search_threads(
        cls,
        query: str,
    ) -> list[dict]:
        """Search threads and replies by query, return a list of matching thread meta."""
        # TODO: Maybe return thread meta like title, author, score, created_at to display in search results directly?
        pass

    @classmethod
    def search_threads_by_tags(cls, tags: list[str]) -> list[dict]:
        pass

    @classmethod
    def delete_thread(cls, thread_pub_id: str) -> bool:
        if not cls.can_update_delete_thread(user_id=1, thread_pub_id=thread_pub_id):
            return False

        if not cls.thread_exists(thread_pub_id=thread_pub_id):
            return False

        # TODO: Delete in db and index.

    @classmethod
    def add_reply(cls, thread_pub_id: str, content: str, user_id: int) -> Reply:
        reply = Reply.objects.create(
            content=content,
            thread_id=Thread.objects.get(public_id=thread_pub_id).id,
            created_by_id=user_id,
        )
        # TODO: Index in search engine.
        return reply

    @classmethod
    def update_reply(cls, reply_pub_id: str, content: str) -> Reply | None:
        if not cls.can_update_delete_reply(user_id=1, reply_pub_id=reply_pub_id):
            return None

        if not cls.reply_exists(reply_pub_id=reply_pub_id):
            return None

        # TODO: Update in db and index.

    @classmethod
    def delete_reply(cls, reply_pub_id: str, user_id: int) -> bool:
        if not cls.can_update_delete_reply(user_id=user_id, reply_pub_id=reply_pub_id):
            return False

        if not cls.reply_exists(reply_pub_id=reply_pub_id):
            return False

        Reply.objects.get(public_id=reply_pub_id).delete()
        # TODO: Delete from search index.

    @classmethod
    def get_replies(cls, thread_pub_id: str) -> list[ThreadSchema]:
        q = Reply.objects.filter(thread__public_id=thread_pub_id)
        return [r.as_schema() for r in q]
