from rest_framework import viewsets
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from rentlist.models import *
from django.shortcuts import get_object_or_404
from rest_framework import exceptions
import dateutil

class SenyViewSet(viewsets.ModelViewSet):
    """
        filterable_by should be a list, or tuple. The elements in this iterable should either be lists
        themselves or single objects. If the element is a single object it will be used as a param to filter by.
        If the element is an iterable the filter will be ran on '__'.join(iterable).
        This can be used to denote relationship properties: owner.username === owner__name === [owner, name]
        Or it could be used with django field lookups
        https://docs.djangoproject.com/en/dev/ref/models/querysets/#std:fieldlookup-exact
        ['username', 'exact']    would be case sensitive while username__iexact would be case insensitive
        ['username', 'contains'] would check if the field contains the query param
    """
    filterable_by = None
    order_by = []

    def get_queryset(self, ignore_paging=False):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        assert self.filterable_by is not None, (
            "'%s' should include a 'filterable_by' iterable attribute" % self.__class__.__name__
        )
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
            page_size = self.request.QUERY_PARAMS.get('page_size', None)
            page = self.request.QUERY_PARAMS.get('page', 0)
            filters = {}
            tags = False
            for kw in self.filterable_by:
                val = None
                if kw == list(kw):
                    val = self.request.QUERY_PARAMS.get(kw[0], None)
                    kw = '__'.join(kw)
                elif kw == 'tags':
                    val = self.request.QUERY_PARAMS.get('tags', None)
                    if queryset.model is Product:
                        kw = 'tags__text__icontains'
                    elif queryset.model is Advertisement:
                        kw = 'product__tags__text__icontains'
                    else:
                        val = None
                else:
                    val = self.request.QUERY_PARAMS.get(kw, None)
                if val:
                    if kw in ['start__lte', 'end__lte']:
                        val = dateutil.parser.parse(val, fuzzy=True)
                    filters[kw] = val

            queryset = queryset.filter(**filters)

            if page_size and not ignore_paging:
                queryset = Paginator(queryset, page_size)
                queryset = queryset.page(page)

        return queryset


    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def permission_denied(self, request, message="You do not have permission to perform this action."):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        if not request.successful_authenticator:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(message)

    def check_object_permissions(self, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(request, permission.message)

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(request, permission.message)