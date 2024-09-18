# TODO: Search engine wrappers
# TODO: Set search engine in .env -> settings and have wrapper here
import abc


class Search(abc.ABC):
    @abc.abstractmethod
    def search(self, query: str) -> list[dict]:
        pass


class SimpleSearch(Search):
    def search(self, query: str) -> list[dict]:
        pass


class MeilisearchSearch(Search):
    def search(self, query: str) -> list[dict]:
        pass


def get_search_engine() -> Search:
    return SimpleSearch()
