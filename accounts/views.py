from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, get_tokens_for_user, UserProfileSerializer
from books.models import Book
from books.serializers import BookListSerializer
from rest_framework import permissions


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response(
                {
                    "message": "User registered successfully",
                    "tokens": tokens,
                    "user": {
                        "email": user.email,
                        "phone": user.phone,
                        "name": user.name,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        serializer = LoginSerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Login successful",
                "tokens": tokens,
                "user": {
                    "email": user.email,
                    "phone": user.phone,
                    "name": user.name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "is_blocked": user.is_blocked,
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        books = Book.objects.filter(is_published=True)
        serializer = BookListSerializer(books, many=True)
        return Response({
            "message": "Welcome to BookReader API",
            "total_books": books.count(),
            "books": serializer.data
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
