from django_filters.views import FilterView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import AuthorFilter, BookFilter
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


class AuthorList(FilterView):
    template_name = "books/author_filter.html"
    filterset_class = AuthorFilter


class BookList(FilterView):
    template_name = "books/book_filter.html"
    filterset_class = BookFilter


class AuthorViewset(ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filterset_class = AuthorFilter


class BookViewset(ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_class = BookFilter
