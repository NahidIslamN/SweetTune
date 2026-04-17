from django.urls import path
from .views import MyLibraryView, LegentLibraryView

urlpatterns = [
    path('librarys/', MyLibraryView.as_view(), name='librarys'),
    path('librarys/<int:pk>/', MyLibraryView.as_view(), name='librarys'),
    path('legent-librarys/', LegentLibraryView.as_view(), name='legent-librarys'),
]


