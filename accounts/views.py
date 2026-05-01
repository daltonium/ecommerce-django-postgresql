from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    # WHY AllowAny? Registration is public — an unauthenticated user needs to sign up.
    # We're overriding the default IsAuthenticated we set globally in settings.py.

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        # request.data = the JSON body Django parsed from the HTTP request

        if serializer.is_valid():
            # is_valid() runs all field validations:
            # - email format check
            # - password min_length=8
            # - email uniqueness (hits the DB)
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
                # 201 Created = standard HTTP response for "resource was created"
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # 400 Bad Request = invalid input. Errors tell the client exactly what went wrong.


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    # Only logged-in users can see their own profile

    def get(self, request):
        # request.user is automatically set by JWTAuthentication
        # when a valid token is in the Authorization header
        serializer = UserSerializer(request.user)
        return Response(serializer.data)