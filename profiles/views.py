from rest_framework.views import APIView
from .serializers import CustomUserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


# Create your views here.



class MyAccountAPIView(APIView):
    permission_classes=[IsAuthenticated]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    
    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response({
            "success": True,
            "data": serializer.data
        })


    def patch(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Profile partially updated",
                "data": serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

