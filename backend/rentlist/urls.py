from django.conf.urls import url, include
from rentlist import views
from rest_framework.routers import DefaultRouter
from django.contrib import admin

# Create a router and register our viewsets with it.
router = DefaultRouter()
# router.register(r'users', views.UserViewSet
router.register(r'user-profiles', views.UserProfileViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'threads', views.MessageThreadViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'advertisements', views.AdvertisementViewSet)
router.register(r'advertisement-responses', views.AdvertisementResponseViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'images', views.ImageViewSet)
router.register(r'tags', views.TagViewSet)
# The API URLs a    re now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'api/alpha/', include(router.urls)),
    url(r'auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'admin/', include(admin.site.urls)),
    url(r'login/$', views.Login, name="login"),
    url(r'sign_up/$', views.SignUp.as_view(), name="sign_up"),
    url(r'test', views.test),
]
