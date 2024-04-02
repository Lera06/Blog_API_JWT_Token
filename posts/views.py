from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions

from .models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = (IsAuthorOrReadOnly,)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = (IsAuthorOrReadOnly,)
    # permission_classes = [permissions.IsAuthenticated]



