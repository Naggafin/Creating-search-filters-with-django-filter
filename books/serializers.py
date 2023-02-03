from rest_framework import serializers

from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.name")

    class Meta:
        model = Book
        fields = ["id", "title", "author", "genre", "publication_date", "isbn", "price"]


class AuthorSerializer(serializers.ModelSerializer):
    published_books = BookSerializer(many=True)

    class Meta:
        model = Author
        fields = ["id", "name", "published_books"]
