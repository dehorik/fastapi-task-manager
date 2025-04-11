from .base_exceptions import RepositoryError


class ResultNotFound(RepositoryError):
    """
    Когда результат первого запроса должен был использоваться
    во втором запросе, но первый запрос ничего не вернул
    """
    pass
