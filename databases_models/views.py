
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, SetupStorage, String
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# Create your views here.


class MyLibraryView(APIView):
    authentication_classes = [IsAuthenticated, IsAdminUser]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get(self, request):
        if request.user.is_superuser:
            setups = SetupStorage.objects.filter().order_by("-create_at")
        else:
            setups = SetupStorage.objects.filter(user = request.user).order_by("-create_at")
        

        pass