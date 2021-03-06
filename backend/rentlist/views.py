from rest_framework.decorators import detail_route, list_route
from rentlist.serializers import *
from rentlist.models import *
from django.core.paginator import Paginator
from rest_framework.response import Response
from rentlist.permissions import *
from rentlist.viewsets import SenyViewSet
from rest_framework import generics
from django.http import JsonResponse
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import filters

from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

def test(request, *args, **kwargs):
    return HttpResponse("Test")

class UserProfileViewSet(SenyViewSet):
    """
        ## Filterable By: ##
            owner - query by user
        ## Special Endpoints ##
        ### User ###
            /api/version/user-profiles/user
            returns profile of current user


    """
    queryset = UserProfile.objects.all()
    permission_classes = [SenyAuth, UserProfilePermissions]
    serializer_class = UserProfileSerializer
    filterable_by = [['owner', 'username', 'iexact']]

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter(Q(owner=request.user))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)



class AdvertisementViewSet(SenyViewSet):
    """
        ## Important Note: ##
            If lat and long is available please provide that data instead of letting the api generate it from zip.
            This applies to creating Ads, updating ads, and zip_query vs. lat_lon
        ## Filterable By: ##
        + tags - will search to see if ay of this ad's product's tags have a text field equal to this parameter
        + product - search product by id
        + product__owner - search by owner
        + product__type - search by product type: 0 = supply, 2 = demand
        + active - 1 for true 0 for false
        + zip - query by zip code
        + zip_query  (lat_lon is preferred over this) - this will order results based on distance from supplied value. If not provided the results will be
          ordered by distance from the current user's lat, long
        + lat_lon - comma separated lat long used for ordering (similar to zip_query but preferred over it)
        + start - check if the date being queried is greater or equal to start
        + end - check if the date being queried is greater or equal to end

        ## Special Endpoints: ##
        ### Toggle ###
            PUT /advertisements/pk/toggle - activates or deactives advertisement based on current state
        ### User ###
            /api/version/advertisements/user
            Returns all advertisements of current user
        ### Recent ###
            /api/version/advertisements/recent
            Returns the last advertisements that this user has accepted responses for

    """
    queryset = Advertisement.objects.all()
    permission_classes = [SenyAuth, AdvertisementPermissions]
    serializer_class = AdvertisementSerializer
    filterable_by = ['tags', ['product', 'id'], ['product__owner', 'username'], ['start', 'gte'], ['end', 'gte'], 'product__type','active', 'zip']

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
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        ads = self.get_queryset(ignore_paging=True)
        if request.QUERY_PARAMS.get('lat_lon', False):
            lat, long = [float(val) for val in request.QUERY_PARAMS.get('lat_lon').split(',')]
        elif request.QUERY_PARAMS.get('zip_query', False):
            lat, long = get_geo(request.QUERY_PARAMS.get('zip_query'))
        else:
            profile = request.user.profile.get()
            lat, long = profile.lat, profile.long
        ads = ads.extra(select={'distance_from_source': DISTANCE_SELECT % (lat, long, lat)}).order_by('distance_from_source')
        distances = ads.values('distance_from_source')
        for ad in zip(ads, distances):
            ad[0].distance = ad[1]['distance_from_source']
        if page_size:
            ads = Paginator(ads, page_size).page(page)
        serializer = AdvertisementSerializer(ads, many=True, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter(Q(product__owner=request.user))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @list_route(methods=['GET'])
    def recent(self, request, *args, **kwargs):
        queryset = Advertisement.objects.raw("""
        select advertisement.* from rentlist_advertisement as advertisement
        join rentlist_advertisementresponse as response on response.advertisement_id = advertisement.id
        where response.accepted=1 and response.owner_id={0}
        limit 15
        """.format(request.user.id))
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)


class MessageViewSet(SenyViewSet):
    """
        ## Filterable by: ##
        + new - 1 for true 0 for false
        + source/destination - username
        + search - checks if title, content, source, destination contain given query string

        ## Special Endpoints ##
        ### new ###
            /api/version/messages/new
            Creates a new thread and message at same time.
        ### User ###
            /api/version/messages/user
            Return all message the current user is involved in.
        ### Read ###
            get /api/version/messages/user/id/read
            Marks message as not new and returns the new object.
    """
    queryset = Message.objects.all()
    permission_classes = [SenyAuth, MessagePermissions]
    serializer_class = MessageSerializer
    filterable_by = ['new', ['destination', 'username'], ['source', 'username']]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('destination__username', 'source__username', 'thread__title', 'content')

    def get_serializer_class(self):
        if self.action in ['new']:
            return MessageWithThreadSerializer
        if self.action in ['response']:
            return MessageWithThreadAndResponseSerializer
        return self.serializer_class

    @list_route(methods=['POST', 'GET'], permission_classes=permission_classes)
    def new(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter(Q(source=request.user) | Q(destination=request.user))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @list_route(methods=['POST', 'GET'])
    def response(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @detail_route(methods=['GET'])
    def read(self, request, pk=None):
        message = self.get_object()
        message.new = False
        message.save()
        return Response(self.get_serializer_class()(message).data)


# todo implement a @list_route function called with_thread. it should use the MessageWithThread serializer instead.


class ImageViewSet(SenyViewSet):
    """
        ## Not Filterable ##
        ## Special Endpoints ##
            /api/version/images/user
            returns all images of current user

            /api/version/images/product
            Add an image to an existing product
    """
    queryset = Image.objects.all()
    permission_classes = [SenyAuth, ImagePermissions]
    serializer_class = ImageSerializer
    filterable_by = []

    def get_serializer_class(self):
        if self.action in ['product']:
            return ImageForProductSerializer
        return self.serializer_class

    @list_route(methods=['POST', 'GET'], permission_classes=permission_classes)
    def product(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter(Q(owner=request.user))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)



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
        ### /api/version/products/new###
            allows you to add a product and upload an image as display_image

        ### User ###
            /api/version/products/user
            return all products owned by current user

        ### Reviewable ###
            /api/version/products/reviewable
            return products reviewable by current user

        ### Recurring Advertisements ###
            POST /api/version/products/<pk>/recurringAdvertisement/ -- this endpoint will create multiple advertisements for a product

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

    def get_serializer_class(self):
        if self.action in ['new'] or self.request.method in ['GET']:
            return ProductWithImageSerializer
        return self.serializer_class

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
            geo = get_geo(zip_cde)
        else:
            geo = request.POST['lat'], request.POST['long']
        recurrences = getRecurrenceDates(request)
        for recurrence in recurrences:
            Advertisement(product_id=pk, zip=zip_cde, start=recurrence[0], end=recurrence[1],
                          active=1, lat=geo[0], lon=geo[1]).save()
        return JsonResponse(recurrences, safe=False)

    @list_route(methods=['PUT', 'GET'])
    def new(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter(Q(owner=request.user))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def reviewable(self, request, *Args, **kwargs):
        query_set = Product.objects.raw("""
        select distinct product.* from rentlist_product as product
        join rentlist_advertisement as ad on product.id = ad.product_id
        join rentlist_advertisementresponse as response on response.advertisement_id = ad.id
        where response.accepted=1 and response.owner_id = {0} and product.owner_id != {0}
        and (select count(*) from rentlist_product
	         join rentlist_review on rentlist_product.id = rentlist_review.product_id
             where rentlist_review.owner_id = {0}
             and product.id = rentlist_review.product_id) = 0
        """.format(request.user.id))
        serializer = self.get_serializer(data=query_set, many=True)
        serializer.is_valid()
        return Response(serializer.data)

class AdvertisementResponseViewSet(SenyViewSet):
    """
        ## Filterable By: ##
        + owner -- query by owner's username
        + advertisement -- query by advertisements'd id
        + accepted -- 1 for true and 0 for false
        + reviewed -- 1 for true and 0 for false
        + deadline__lte -- query such that supplied value is less than or equal to response's deadline
        + deadline__gte -- query such that supplied value is greater than or equal to response's deadline

        ## Special Endpoints ##
        ### User ###
            /api/version/advertisement-responses/user
            returns all responses to and from current user
        ### Pending ###
            /api/version/advertisement-responses/pending
            returns all responses sent to this user that are pending acceptance
        ### Accept ###
            /api/version/advertisement-responses/pk/accept
            Sets accepted to true for a specific response and makes sure all the rest are false.
    """
    queryset = AdvertisementResponse.objects.all()
    permission_classes = [SenyAuth, AdvertisementResponsePermissions]
    serializer_class = AdvertisementResponseSerializer
    filterable_by = [['owner', 'username'], ['advertisement', 'id'], 'accepted', 'reviewed',
                     'deadline__lte', 'deadline__gte']

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def pending(self, request, *args, **kwargs):
        queryset = AdvertisementResponse.objects.raw("""
        SELECT response.* FROM rentlist_advertisementresponse as response
        join rentlist_advertisement as advertisement on advertisement.id = response.advertisement_id
        join rentlist_product as product on advertisement.product_id = product.id
        where product.owner_id = {0}
        and (select count(*) from rentlist_advertisementresponse
	         where advertisement_id=advertisement.id and accepted=1) = 0
	""".format(request.user.id))
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter(Q(owner=request.user) | Q(advertisement__product__owner=request.user)
        | Q(deadline__gte=datetime.now()))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @detail_route(methods=['PUT', 'GET'])
    def accept(self, request, pk=None):
        response = self.get_object()
        for _response in response.advertisement.responses.filter(~Q(id=response.id)):
            _response.accepted = False
            _response.save()
        response.accepted = True
        response.save()
        response.advertisement.active = False
        response.advertisement.save()
        serializer = self.get_serializer(response)
        return Response(serializer.data)




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

        ## Specialized Endpoints ##
        ### User ###
            /api/version/reviews/user
            returns all reviews to/from this user
    """
    queryset = Review.objects.all()
    permission_classes = [SenyAuth, ReviewPermissions]
    serializer_class = ReviewSerializer
    filterable_by = [['owner', 'username'], ['product', 'id'], 'created_at__lte', 'created_at__gte',
                     ['title', 'icontains'], ['content', 'icontains'], ['rating', 'lte'], ['product__owner', 'username']]

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter(Q(owner=request.user) | Q(product__owner=request.user))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user_supply(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter((Q(owner=request.user) | Q(product__owner=request.user) )
        & Q(product__type=0))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user_demand(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter((Q(owner=request.user) | Q(product__owner=request.user))
            & Q(product__type=2))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)



class MessageThreadViewSet(SenyViewSet):
    """
        ## Filterable By: ##
        + created_at__lte -- query such that supplied value is less than or equal to created_at
        + created_at__gte -- query such that supplied value is greater than or equal to created_at
        + responder -- query based on responder's username
        + title -- query for threads with a title that contains supplied value
        + creator -- query based on creator's username

        ## Special Endpoints ##
        ### User ###
            /api/version/threads/user
            return all threads that the current user is involved in
        ### Read ###
            /api/version/threads/id/read
            marks all messsages in the thread as read then returns the thread
    """
    queryset = MessageThread.objects.all()
    permission_classes = [SenyAuth]
    serializer_class = MessageThreadSerializer
    filterable_by = ['created_at__lte', 'created_at__gte', ['responder', 'username'], ['title', 'icontains'],
                    ['creator', 'username']]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'creator__username', 'responder__username')

    @list_route(methods=['GET'], permission_classes=permission_classes)
    def user(self, request, *args, **kwargs):
        page_size = self.request.QUERY_PARAMS.get('page_size', None)
        page = self.request.QUERY_PARAMS.get('page', 0)
        queryset = self.get_queryset(ignore_paging=True).filter(Q(creator=request.user) | Q(responder=request.user))
        if page_size:
            queryset = Paginator(queryset, page_size).page(page)
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        return Response(serializer.data)

    @detail_route(methods=['GET', 'PUT'])
    def read(self, request, pk=None):
        thread = self.get_object()
        for message in thread.messages.all():
            message.new = False
            message.save()
        return Response(self.get_serializer_class()(thread).data)

class SignUp(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = ()


@csrf_exempt
def Login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            return JsonResponse({'client_id': user.application_set.first().client_id,
                                 'client_secret': user.application_set.first().client_secret}, safe=False)
    #         # Redirect to a success page.
    #     else:
    #         # Return a 'disabled account' error message
    # else:
    #     # Return an 'invalid login' error message

# class Login(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = LoginSerializer
#     authentication_classes = (BasicAuthentication,)
#
#     def get_queryset(self):
#         return [self.request.user]
