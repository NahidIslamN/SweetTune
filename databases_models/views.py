
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, SetupStorage, String
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from SweetTune.pagination import CustomPagination

# Create your views here.


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class MyLibraryView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return SetupStorage.objects.all().order_by("-create_at")
        return SetupStorage.objects.filter(user=request.user).order_by("-create_at")

    def get(self, request):
        setups = self.get_queryset(request)

        paginator = CustomPagination()
        page = paginator.paginate_queryset(setups, request)
        serializer = SetupStorageSerializer(page, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = SetupStorageSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(user=request.user)  # attach user automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def put(self, request, pk):
        setup = get_object_or_404(SetupStorage, pk=pk)

    
        if not request.user.is_superuser and setup.user != request.user:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        serializer = SetupStorageSerializer(setup, data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        setup = get_object_or_404(SetupStorage, pk=pk)


        if not request.user.is_superuser and setup.user != request.user:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        setup.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_200_OK)



class LegentLibraryView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self, request):
        
        return SetupStorage.objects.filter(is_public =True,is_varified =True).order_by("-create_at")
        

    def get(self, request):
        setups = self.get_queryset(request)

        paginator = CustomPagination()
        page = paginator.paginate_queryset(setups, request)
        serializer = LegentSetupStorageSerializer(page, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)
