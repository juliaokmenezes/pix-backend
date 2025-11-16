from rest_framework.pagination import CursorPagination
class MyCustomPagination(CursorPagination):
    page_size = 10
    ordering='id'