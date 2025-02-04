from django.shortcuts import render
from django.db.models.aggregates import Count
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import (
    Category,
    Item,
    Location,
    Supply,
    Store,
    StockMovement,
    ReturnRecall,
    ItemImage,
)
from .serializers import (
    CategorySerializer,
    ItemSerializer,
    SupplySerializer,
    StoreSerializer,
    LocationSerializer,
    StockMovementSerializer,
    ReturnRecallSerializer,
    ItemImageSerializer,
)

# Create your views here.


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(items_count=Count("items")).all()
    serializer_class = CategorySerializer


class ItemViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = Item.objects.all()
        category_id = self.request.query_params.get("category_id")
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    serializer_class = ItemSerializer


class SupplyViewSet(ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer


class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class StockMovementViewSet(ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer


class ItemImageViewSet(ModelViewSet):
    queryset = ItemImage.objects.all()
    serializer_class = ItemImageSerializer
