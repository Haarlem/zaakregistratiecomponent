from .registry import proxy_registry


def to_proxy_obj(django_obj):
    """
    Convert a Django object to a Proxy object.
    :param django_obj Django ORM object
    :return An instantiated proxy model based on the django object.
    """
    django_model = django_obj.__class__
    proxy_model = proxy_registry.get_proxy_model(django_model)

    return proxy_model.from_django_obj(django_obj)
