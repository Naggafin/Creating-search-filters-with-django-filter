from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)


class Book(models.Model):
    class Genres(models.TextChoices):
        HORROR = ("hor", "Horror")
        ROMANCE = ("rom", "Romance")
        ADVENTURE = ("adv", "Adventure")
        FANTASY = ("fan", "Fantasy")
        SCIFI = ("sci", "Science Fiction")
        NONFICTION = ("non", "Non-fiction")

    title = models.CharField(max_length=100)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="published_books"
    )
    genre = models.CharField(max_length=3, choices=Genres.choices)
    publication_date = models.DateField()
    isbn = models.CharField("ISBN", max_length=13)
    price = models.DecimalField(max_digits=5, decimal_places=2)
