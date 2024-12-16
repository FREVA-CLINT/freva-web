from urllib.parse import urljoin

import requests
from django.conf import settings
from django.http import StreamingHttpResponse
from django.views import View


class ChatBotProxy(View):
    def get(self, request, *args, **kwargs):
        path = request.path
        base_url = urljoin(settings.CHAT_BOT_URL, path)
        params = request.GET.dict()

        # adding bot auth key and freva conf
        params["auth_key"] = settings.CHAT_BOT_AUTH_KEY
        params["freva_config"] = settings.CHAT_BOT_FREVA_CONFIG

        try:
            upstream_response = requests.get(base_url[:-1], params=params, stream=True)
            upstream_response.raise_for_status()
        except requests.RequestException as e:
            return StreamingHttpResponse(
                f"Error while connecting to the external API: {str(e)}",
                status=502,
            )

        # Stream the content of the external API to the Django response
        def stream():
            for chunk in upstream_response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        response = StreamingHttpResponse(
            stream(), content_type=upstream_response.headers.get("Content-Type")
        )
        response["Content-Disposition"] = upstream_response.headers.get(
            "Content-Disposition", "inline"
        )

        return response
