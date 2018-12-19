from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AuthenticatedUser(APIView):
    serializer_class = UserSerializer

    def get(self, request):

        if request.user.is_authenticated():
            return Response(self.serializer_class(request.user).data)
        return Response({})#False)
