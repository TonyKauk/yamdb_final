from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from reviews.models import (
    Category, Genre,
    Review, Title, User
)
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAdminModerAuthorAuthenticatedOrReadOnly
)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, SignupSerializer, TitleGetSerializer,
    TitleSerializer, TokenSerializer, UserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdmin)
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False, methods=('GET', 'PATCH'),
        url_path='me', permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)

        if request.method != 'PATCH':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = UserSerializer(
            user,
            context={'request': request},
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class SingupViewSet(viewsets.ModelViewSet):
    querryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email').lower()
        user, created = User.objects.get_or_create(
            email=email,
            username=username
        )
        confirmation_code = (
            PasswordResetTokenGenerator().make_token(user)
        )
        message = f'Код подтверждения - {confirmation_code}'
        send_mail(
            'Ваш код подтверждения',
            message,
            settings.EMAIL_FROM,
            (email, )
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class TokenViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request):
        code_test = PasswordResetTokenGenerator()
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data.get('username')
        )
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if not code_test.check_token(user, confirmation_code):
            return Response(
                {'confirmation_code': ['Код не действителен!']},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.is_active = True
        user.save()
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnly
    ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnly
    ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnly
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        else:
            return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModerAuthorAuthenticatedOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title)
        serializer.save(author=self.request.user, review_id=review.id)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModerAuthorAuthenticatedOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title_id=title.id)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(method='PUT')
        return super().update(request, *args, **kwargs)
