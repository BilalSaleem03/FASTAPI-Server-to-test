# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. GET route - Fetch all products
    path('api/django-api/', views.ProductListView.as_view(), name='product-list'),
    
    # 2. POST route - Create a new product
    path('api/django-api/create/', views.ProductCreateView.as_view(), name='product-create'),
    
    # 3. GET route - Fetch specific product by ID
    path('api/django-api/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # 4. PATCH route - Update partial product data
    path('api/django-api/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
]

# views.py (corresponding views)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ProductListView(APIView):
    def get(self, request):
        return Response({'products': ['Product 1', 'Product 2']}, status=status.HTTP_200_OK)

class ProductCreateView(APIView):
    def post(self, request):
        name = request.data.get('name')
        return Response({'message': f'Product {name} created'}, status=status.HTTP_201_CREATED)

class ProductDetailView(APIView):
    def get(self, request, pk):
        return Response({'id': pk, 'name': f'Product {pk}'}, status=status.HTTP_200_OK)

class ProductUpdateView(APIView):
    def patch(self, request, pk):
        return Response({'message': f'Product {pk} updated'}, status=status.HTTP_200_OK)