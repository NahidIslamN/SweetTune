from django.urls import path
from .views import *

urlpatterns = [
    path('me/', MyAccountAPIView.as_view(), name="profiles")
]
