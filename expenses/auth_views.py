from rest_framework.views import APIView
from .auth_serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "id":user.id,
            "username": user.username,
            "message": "User Created Successfully"
            }, status=status.HTTP_201_CREATED)