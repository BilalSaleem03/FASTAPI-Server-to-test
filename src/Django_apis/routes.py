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


