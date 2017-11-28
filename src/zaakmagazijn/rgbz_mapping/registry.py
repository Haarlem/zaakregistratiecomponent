class ProxyRegistry:
    """
    A simple registry of Proxy models. Similar to Django's Apps registry.

    Used to determine ProxyModel from Django Models.
    """
    def __init__(self):
        self.django_to_proxy = {}

    def register_proxy_model(self, proxy_model):
        self.django_to_proxy[proxy_model.model] = proxy_model

    def get_proxy_model(self, model):
        return self.django_to_proxy[model]


proxy_registry = ProxyRegistry()
