from rest_framework.response import Response
from rest_framework.views import APIView

from base.exceptions import UserNotFoundError
from base.Users import OpenIdUser

from .serializers import UserSerializer


class AuthenticatedUser(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        if request.user.is_authenticated:
            try:
                user = OpenIdUser(request.user.username, request.session.get("user_home_dir", ""))
            except UserNotFoundError:
                user = None
            return Response(
                self.serializer_class(request.user, context={"user": user}).data
            )
        return Response({})  # False)
