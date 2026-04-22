from django.urls import path
from .views import *

urlpatterns = [
    #all done
    path('amazon-products/', AmazonProductSearchAPIView.as_view(), name='my-products')
 
    
]
