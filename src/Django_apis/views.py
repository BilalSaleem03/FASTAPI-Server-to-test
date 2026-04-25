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