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
