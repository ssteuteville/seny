from rest_framework.decorators import detail_route
from rentlist.serializers import *
from rentlist.models import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rentlist.permissions import *
from rentlist.viewsets import SenyViewSet
from rest_framework import generics
from rest_framework.authentication import BasicAuthentication
from django.http import JsonResponse
from rest_framework import mixins, viewsets

class UserProfileViewSet(SenyViewSet):
    """
        ## Filterable By: ##
            owner - query by user
        ### No Special Endpoints ###

    """
    queryset = UserProfile.objects.all()
    permission_classes = [SenyAuth, UserProfilePermissions]
    serializer_class = UserProfileSerializer
    filterable_by = [['owner', 'username', 'iexact']]


class AdvertisementViewSet(SenyViewSet):
    """
        ## Important Note: ##
            If lat and long is available please provide that data instead of letting the api generate it from zip.
            This applies to creating Ads, updating ads, and zip_query vs. lat_lon
        ## Filterable By: ##
        + tags - will search to see if ay of this ad's product's tags have a text field equal to this parameter
        + product - search product by id
        + product__owner - search by owner
        + active - 1 for true 0 for false
        + zip - query by zip code
        + zip_query  (lat_lon is preferred over this) - this will order results based on distance from supplied value. If not provided the results will be
          ordered by distance from the current user's lat, long
        + lat_lon - comma separated lat long used for ordering (similar to zip_query but preferred over it)

        ## Special Endpoints: ##
        ### Toggle ###
            PUT /advertisements/pk/toggle - activates or deactives advertisement based on current state

    """
    queryset = Advertisement.objects.all()
    permission_classes = [SenyAuth, AdvertisementPermissions]
    serializer_class = AdvertisementSerializer
    filterable_by = ['tags', ['product', 'id'], ['product__owner', 'username'], 'active', 'zip']

    @detail_route(methods=['PUT'], permission_classes=permission_classes)
    def toggle(self, request, pk=None):
        ad = self.get_object()
        if ad.active:
            ad.active = 0
        else:
            ad.active = 1
        ad.save()
        serializer = AdvertisementSerializer(ad)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        ads = self.get_queryset()
        if request.QUERY_PARAMS.get('lat_lon', False):
            lat, long = [float(val) for val in request.QUERY_PARAMS.get('lat_lon').split(',')]
        elif request.QUERY_PARAMS.get('zip_query', False):
            lat, long = get_geo(request.QUERY_PARAMS.get('zip_query'))
        else:
            profile = request.user.profile.get()
            lat, long = profile.lat, profile.long
        ads = ads.extra(select={'distance_from_source': DISTANCE_SELECT % (lat, long, lat)}).order_by('distance_from_source')
        distances = ads.values('distance_from_source')
        for ad in zip(ads,distances):
            ad[0].distance = ad[1]['distance_from_source']
        serializer = AdvertisementSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)


class MessageViewSet(SenyViewSet):
    """
        ## Filterable by: ##
        + new - 1 for true 0 for false

        ## No Special Endpoints ##
    """
    queryset = Message.objects.all()
    permission_classes = [SenyAuth, MessagePermissions]
    serializer_class = MessageSerializer
    filterable_by = ['new']


class ImageViewSet(SenyViewSet):
    """
        ## Not Filterable ##
        ## No Special Endpoints ##
    """
    queryset = Image.objects.all()
    permission_classes = [SenyAuth, ImagePermissions]
    serializer_class = ImageSerializer
    filterable_by = []


class ProductViewSet(SenyViewSet):
    """
        ## Filterable By: ##
        + tags - will search all of this product's tags for specified text
        + price__gt(e) - query products in which specified value is greater than price, use e option for >=
        + price__lt(e) - query products in which specified value is less than price, use e option for >=
        + description - search for products with a description containing specified text
        + type = 0 for supply and 1 for demand
        + owner = search by owner's username

        ## Special EndPoints: ##
        ### /api/alpha/products-img-ref/ ###
            allows you to add/update a product using an existing image as display_image

        ### Recurring Advertisements ###
            POST /api/alpha/products/<pk>/recurringAdvertisement/ -- this endpoint will create multiple advertisements for a product

            Parameters:

            zip : zipcode the ad is available in (either zip or lat and long)

            lat : latitude of ad (either lat and long or zip)

            long : longitude of ad (either lat and long or zip)

            freq: can be weekly, daily, monthly (required)

            byweekday: should be a comma separated list of any of these: mo,tu,we,th,fr,sa,su

            bymonthday: should be integers representing dates in month (required bymonth param)

            bymonth: should be an integer represeting month

            byhour: should be comma separated list of military times ads should start

            dtstart: the date of the first cccurence

            until: date of last occurence

            duration: number of units the ad should last

            duration_metric: units duration is measured in.. can be day week or month
    """
    queryset = Product.objects.all()
    permission_classes = [SenyAuth, ProductPermissions]
    serializer_class = ProductSerializer
    filterable_by = ['tags', 'price__gt', 'price__gte', 'price__lt', 'price__lte', ['description', 'icontains'],
                     'type', ['owner', 'username']]

    @detail_route(methods=['POST'])
    def recurringAdvertisement(self, request, pk=None):
        """
            product_id : the product we are adding ads for. (required)
            zip : zipcode the ad is available in (required)
            freq: can be weekly, daily, monthly (required)
            byweekday: should be a comma separated list of any of these:
                mo,tu,we,th,fr,sa,su
            bymonthday: should be integers representing dates in month (required bymonth param)
            bymonth: should be an integer represeting month
            byhour: should be comma separated list of military times ads should start
            dtstart: the date of the first cccurence
            until: date of last occurence
            duration: number of units the ad should last
            duration_metric: units duration is measured in.. can be day week or month

            example post data:
                    {
                        "dtstart": "1/29/15",
                        "until": "2/21/15",
                        "duration": "2",
                        "byweekday": "tu,th",
                        "duration_metric": "day",
                        "freq": "weekly",
                        "byhour": "17",
                        "product_id": "10",
                        "zip": "95928"
                    }
                translation: every tuesday and thursday at 5pm between 1/29/15 and 2/21/15

                todo: update advertisement model in uml diagram

        """
        geo = None
        zip_cde = request.POST.get('zip', None)
        if zip_cde:
            del request.POST['zip']
            geo = get_geo(zip_cde)
        else:
            geo = request.POST['lat'], request.POST['long']
            del request.POST['lat']
            del request.POST['long']
        recurrences = getRecurrenceDates(request)
        for recurrence in recurrences:
            Advertisement(product_id=pk, zip=zip_cde, start=recurrence[0], end=recurrence[1],
                          active=1, lat=geo[0], lon=geo[1]).save()
        return JsonResponse(recurrences, safe=False)


class ExistingImageProductWriteViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    """
        ### Specialized endpoint that allows product's to be created using image that was already uploaded as display_image ###
    """
    queryset = Product.objects.all()
    serializer_class = ExistingImageProductCreateSerializer
    permission_classes = [SenyAuth, ProductPermissions]


class AdvertisementResponseViewSet(SenyViewSet):
    """
        ## Filterable By: ##
        + owner -- query by owner's username
        + advertisement -- query by advertisements'd id
        + accepted -- 1 for true and 0 for false
        + reviewed -- 1 for true and 0 for false
        + deadline__lte -- query such that supplied value is less than or equal to response's deadline
        + deadline__gte -- query such that supplied value is greater than or equal to response's deadline

        ## No Special Endpoints ##
    """
    queryset = AdvertisementResponse.objects.all()
    permission_classes = [SenyAuth, AdvertisementResponsePermissions]
    serializer_class = AdvertisementResponseSerializer
    filterable_by = [['owner', 'username'], ['advertisement', 'id'], 'accepted', 'reviewed',
                     'deadline__lte', 'deadline__gte']


class TagViewSet(SenyViewSet):
    """
        ## Filterable By: ##
        + text -- check if tag's text contains supplied value

        ## No Special Endpoints ##
    """
    queryset = Tag.objects.all()
    permission_classes = [SenyAuth, TagPermissions]
    serializer_class = TagSerializer
    filterable_by = [['text', 'icontains']]


class ReviewViewSet(SenyViewSet):
    """
        ## Filterable By: ##
        + owner -- query based on owner's username
        + product -- query based on product's id
        + created_at__lte -- query such that supplied value is less than or equal to created_at
        + created_at__gte -- query such that supplied value is greater than or equal to created_at
        + title -- query based on whether title contains supplied text
        + content -- query based on whether content contains supplied text
        + rating -- query for reviews with a rating greater than or equal to supplied values

        ## No Specialized Endpoints ##
    """
    queryset = Review.objects.all()
    permission_classes = [SenyAuth, ReviewPermissions]
    serializer_class = ReviewSerializer
    filterable_by = [['owner', 'username'], ['product', 'id'], 'created_at__lte', 'created_at__gte',
                     ['title', 'icontains'], ['content', 'icontains'], ['rating', 'lte']]


class MessageThreadViewSet(SenyViewSet):
    """
        ## Filterable By: ##
        + created_at__lte -- query such that supplied value is less than or equal to created_at
        + created_at__gte -- query such that supplied value is greater than or equal to created_at
        + responder -- query based on responder's username
        + title -- query for threads with a title that contains supplied value
        + creator -- query based on creator's username

        ## No Special Endpoints ##
        ## No Special Endpoints ##
    """
    queryset = MessageThread.objects.all()
    permission_classes = [SenyAuth]
    serializer_class = MessageThreadSerializer
    filterable_by = ['created_at__lte', 'created_at__gte', ['responder', 'username'], ['title', 'icontains'],
                    ['creator', 'username']]


class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (IsAuthenticatedOrCreate,)


class Login(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    authentication_classes = (BasicAuthentication,)

    def get_queryset(self):
        return [self.request.user]
