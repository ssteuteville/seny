import django_filters
from rentlist.serializers import *


class UserProfileFilter(django_filters.FilterSet):
    owner = django_filters.CharFilter(name="owner__username")

    class Meta:
        model = UserProfile
        fields = ['owner']


class ImageFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(name='text', lookup_type='icontains')

    class Meta:
        model = Image
        fields = ['titles']


class ProductFilter(django_filters.FilterSet):
    max_price = django_filters.NumberFilter(name='price', lookup_type='lte')
    min_price = django_filters.NumberFilter(name='price', lookup_type='gte')
    description = django_filters.CharFilter(name='description', lookup_type='icontains')
    owner = django_filters.CharFilter(name='owner__username')

    class Meta:
        model = Product
        fields = ['max_price', 'min_price', 'description', 'type', 'owner']