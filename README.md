Using Django Filter to create a Filterable Book Catalog

In many Django web applications, filtering querysets based on user input is a critical functionality. Applications such as e-commerce websites, library catalogs, and plenty others often require the ability for users to specify search criteria to narrow down the data they are presented with. This tutorial will guide you through the process of creating both a user interface for searching and a search web API using Django Filter.

In this article, you'll learn the following:
..* What Django Filter is and why it's useful
..* How to create FilterSets for your models
..* Creating views that can use FilterSets to filter data they return

This article assumes that you have a basic understanding of Python, Django, Django REST Framework, and HTML.

# What is Django Filters?
Django Filters is a third-party library for Django that allows you to easily filter querysets based on user input. It provides a convenient method of filtering data using URL query parameters and offers a specific view class to manage this process. The library also offers an automatic form generator that provides a user-friendly interface for users to input their search criteria.

One of the key benefits of using Django Filters is its integration with Django REST Framework, which permits you to add filters to your API endpoints. This library is designed to have an API that is similar to Django's existing ModelForm API, making it intuitive and familiar to work with.

# Setting up the project
First let's setup our virtual environment and install everything we need for the project we're going to create:

```bash
python3 -m virtualenv .venv/
. .venv/bin/activate
pip install django django-filter djangorestframework
```

Next, let's create a new Django project using the following command in the terminal:

```bash
django-admin startproject bookcatalog
cd bookcatalog/
python manage.py startapp books
```

Finally, let's add `django-filters` and `rest_framework` to our list of installed apps, configure our templates directory, set our filter backend and add a browsable renderer to Django REST Framework, and then add our `books` app to the URL patterns for when we make our views:

```python
# bookcatalog/settings.py

DEBUG = True

INSTALLED_APPS = [
	...
	'rest_framework',
	'django_filters',
	...
]

TEMPLATES = [
	{
		...
		'DIRS': [BASE_DIR / 'templates'],  # this works if BASE_DIR is a Path object; if not, you will use os.path.join()
		...
	},
]

REST_FRAMEWORK = {
	...
	'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
	'DEFAULT_RENDERER_CLASSES': [
		'rest_framework.renderers.JSONRenderer',
		'rest_framework.renderers.BrowsableAPIRenderer',
	],
	...
}


# bookcatalog/urls.py

from django.urls import include, path

url_patterns = [
	...
	path("books/", include("books.urls")),
	...
]
```

Our project is now setup and we're ready to continue.

# Creating a model and a serializer
To get started, we will define two models that we can use to filter data: Author and Book. We'll create some basic fields on them that we'll be able to filter for later, and we will create a ForeignKey relationship between the Book and Author models so that we can easily retrieve a set of books for any given author. To do this, add the following code to the models.py file within the books app:

```
# books/models.py

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
```

Now we need to define the serializers for our models so that we can utilize Django REST Framework and later create a filterable web API. We'll define a serializer for both the Author and Book models. The BookSerializer is used as a nested serializer in AuthorSerializer (as indicated by the `published_books` field) for the convenience of the end user. Without a nested serializer, Django REST Framework would only serialize the primary key field, which is `id` by default. With the nested serializer defined, it will serialize all of the fields defined in the BookSerializer for each Book in the Author's `published_books` set into a JSON array. Create a serializers.py file in the books app folder and add the following code:

```python
# books/serializers.py

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
```

With the models and serializers properly set up, we're now ready to create our FilterSet and views.

# Creating the FilterSet
At the heart of Django Filters lies the FilterSet class, which functions similarly to a Django ModelForm class but is used to filter a model's queryset rather than create or update a model instance. The FilterSet can be configured to filter the queryset based on user input either by defining the filters explicitly or by using a Meta class. There are two ways to define which fields to filter in a FilterSet Meta class: by providing a list of field names, which will always filter using `__exact`, or by providing a dictionary where the key is the field name and the value is a list of lookup expressions. The latter approach allows for more nuanced filtering, such as filtering CharFields by `__icontains` instead of `__exact`.

It's also worth noting that filters inside of a FilterSet can span relationships using the double underscore syntax. For instance, to filter the books by author's name, you can use `author__name` as a filter field in the FilterSet class.

By default, fields within the FilterSet are optional, unlike Django Forms where all fields are required by default. This is because the user may not want to search by all available parameters, but only a few. The FilterSet class can handle this by intelligently not including filters that have not been supplied a value.

In this tutorial, we will create FilterSets for Author and Book: AuthorFilter and BookFilter. BookFilter filters the title and author using `__icontains`, with author being an explicitly defined field so we can have it span relationships, and keeps genre with `__exact` as it has accompanying choices. It will also have two explicitly defined fields for specifying price: `min_price` and `max_price`. AuthorFilter will only filter an author's name by using `__icontains`. We will use the FilterSet class from `django_filters.restframework` to allow for REST API usage, rather than the standard FilterSet class from `django_filters`. To do so, create a file filters.py within the books app and add the code provided:

```python
# books/filters.py

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
```

# Creating a FilterView and ListAPIView
Now that we've created our FilterSet classes, we'll need to create views so we can actually use them. Django Filter provides a FilterView class, which we can use to easily implement a fully-featured view with filter capabilities. It functions similarly to Django's generic ListView class. While you can also use function-based views, we'll be using class-based views in this tutorial for their ease of implementation and comprehensive "batteries included" approach. In addition to FilterView, we'll also use Django REST Framework's ReadOnlyModelViewSet class to implement filtering via web API. Add the following code to the views.py file in your books app to render the filtered books, and another view to return a filtered list of books through the web API.

```python
# books/views.py

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
```

And that's it. Just four classes and a mere ten lines of code between them and we've got our filterable views for not one, but two models. It's incredible how simple it is to implement filtering with Django Filter. Now we need to create our URL patterns. We'll be creating two URL paths to our FilterViews and two API routes to our API endpoints with Django REST Framework's DefaultRouter class, with the router being pathed to /api. To keep our URL namespaced, the empty pattern will match a RedirectView that will redirect the browser to /books by default. Create a urls.py for the books app and add the following code in the file:

```python
# books/urls.py

from django.urls import include, path
from django.views.generic.base import RedirectView
from rest_framework import routers
from . import views

app_name = "books"

router = routers.DefaultRouter()
router.register(r"authors", views.AuthorViewset)
router.register(r"books", views.BookViewset)

urlpatterns = [
	path("", RedirectView.as_view(pattern_name="books:book_list"), name="index"),
	path("authors/", views.AuthorList.as_view(), name="author_list"),
	path("books/", views.BookList.as_view(), name="book_list"),
	path("api/", include(router.urls)),
]
```

# Creating a Template
Now that we have our FilterSets, our views, and our URL patterns, we need to create an HTML template to render. Create a "templates" folder in the base directory of the project, and then make another folder inside of that called "books". Make a file called "base.html" under the "templates" folder, and two files called "book_filter.html" and "author_filter.html" under "templates/books/" and add the following code to the three files:

```html
# templates/base.html

<!DOCTYPE html>
<html>
<head>
	<title>Book Catalog</title>
</head>
<body>
	{% block header %}
	<header>
		<a href="{% url 'books:book_list' %}">Search catalog by books</a>
		<a href="{% url 'books:author_list' %}">Search catalog by authors</a>
	</header>
	{% endblock %}
	{% block content %}
	{% endblock %}
</body>
</html>


# templates/book/book_filter.html

{% extends 'base.html' %}

{% block content %}
<main>
	<h1>Books</h1>
	<form action="{% url 'books:book_list' %}" method="get">
		{{ filter.form.as_div }}
		<button type="submit">Search</button>
	</form>
	<table>
		<thead>
			<tr>
				<th>Title</th>
				<th>Author</th>
				<th>Genre</th>
				<th>Publication Date</th>
				<th>ISBN</th>
				<th>Price</th>
			</tr>
		</thead>
		<tbody>
			{% for book in filter.qs %}
				<tr>
					<td>{{ book.title }}</td>
					<td>{{ book.author.name }}</td>
					<td>{{ book.get_genre_display }}</td>
					<td>{{ book.publication_date }}</td>
					<td>{{ book.isbn }}</td>
					<td>${{ book.price }}</td>
				</tr>
			{% empty %}
				<tr>
					<td colspan="6">No books to show!</td>
				</tr>
			{% endfor %}
		</tbody>
	</table>
</main>
{% endblock %}


# templates/books/author_filter.html

{% extends 'base.html' %}

{% block content %}
<main>
	<h1>Authors</h1>
	<form action="{% url 'books:author_list' %}" method="get">
		{{ filter.form.as_div }}
		<button type="submit">Search</button>
	</form>
	<table>
		<thead>
			<tr>
				<th>Author</th>
				<th>Published books</th>
			</tr>
		</thead>
		<tbody>
			{% for author in filter.qs %}
				<tr>
					<td>{{ author.name }}</td>
					<td>
						{% for book in author.published_books.all %}
							{{ book.title }}<br>
						{% endfor %}
					</td>
				</tr>
			{% empty %}
				<tr>
					<td colspan="2">No authors to show!</td>
				</tr>
			{% endfor %}
		</tbody>
	</table>
</main>
{% endblock %}
```

# Migrate the Database and Run the Django Server
Now we're almost ready! Run the following command in the terminal to migrate the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

If you've downloaded the project from the github repo, then this will automatically add some initial Book records to the database to make it easier to sample the app.

Run the Django development server using the following command in the terminal:

```bash
python manage.py runserver
```

Open your web browser and navigate to http://localhost:8000/ to view your bookcatalog app. You should be able to filter books by their title, author, genre, publication date, ISBN, and price, and authors by their names. You can test the REST API out by browsing http://localhost:8000/api/.

Congratulations, you have successfully created a Django bookcatalog app with the ability to filter books using django-filter!

This tutorial has provided a basic introduction to using django-filter in a Django project. You can extend this example by adding more fields to the filterset, adding pagination, or styling the HTML with CSS.
