from django.utils import translation


class AdminEnglishMiddleware:
    """
    Force English for Django admin, without changing the site default language.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            translation.activate("en")
            request.LANGUAGE_CODE = "en"
            try:
                response = self.get_response(request)
            finally:
                translation.deactivate()
            return response

        return self.get_response(request)
