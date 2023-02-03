from django_filters import rest_framework as filters

from .models import Author, Book


class AuthorFilter(filters.FilterSet):
    class Meta:
        model = Author
        fields = {
            "name": ["icontains"],
        }


class BookFilter(filters.FilterSet):
    author = filters.CharFilter(field_name="author__name", lookup_expr="icontains")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Book
        fields = {
            "title": ["icontains"],
            "genre": ["exact"],
            "publication_date": ["year", "range"],
            "isbn": ["iexact"],
            "price": ["exact"],
        }
