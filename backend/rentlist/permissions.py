from rest_framework import permissions
from rentlist.models import MessageThread
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated

class SenyAuth(IsAuthenticated):
    message = "Not authenticated"

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


class UserViewSetPermission(permissions.BasePermission):
    safe = ['GET', 'OPTIONS', 'retrieve']

    def has_permission(self, request, view):
        if request.method in self.safe and view.action in self.safe:
            return True
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.username == obj.username:
            return True
        return False


class IsUserOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if getattr(obj, 'username', None) == request.user.username:
            return True
        return request.user.is_superuser()


class IsAuthenticatedOrCreate(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return super(IsAuthenticatedOrCreate, self).has_permission(request, view)


class SenyPermission(permissions.BasePermission):
    message = None


class AdvertisementPermissions(SenyPermission):

    def has_permission(self, request, view):
        self.message = "You must set up your profile before viewing advertisements.."
        profile = request.user.profile.get()
        return profile.lat is not None and profile.long is not None

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            self.message = "Only the owner can edit this advertisement.."
            return request.user.username == obj.product.owner.username
        return True


class UserProfilePermissions(SenyPermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            self.message = "Only the owner can edit this profile.."
            return request.user.username == obj.owner.username
        return True


class MessagePermissions(SenyPermission):

    def has_permission(self, request, view):
        if request.method in ["PUT", "PATCH", "DELETE"]:
            self.message = "Messages can't be edited or deleted."
            return False
        return True

    def has_object_permission(self, request, view, obj):
        cur_user = request.user.username
        self.message = "Only the source or destination user can view a message.."
        if cur_user == obj.thread.creator.username and obj.destination.username == obj.thread.responder.username:
            return True
        if cur_user == obj.thread.responder.username and obj.destination.username == obj.thread.creator.username:
            return True
        return False


class ImagePermissions(SenyPermission):

    message = "Only the user who uploaded the image can modify/delete it."

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return request.method in ["PUT", "PATCH", "DELETE"] and obj.owner.username == request.user.username


class ProductPermissions(SenyPermission):

    message = "Only the user who created this product may edit or delete it."

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        return request.method in ['PUT', 'DELETE', 'PATCH'] and request.user.username == obj.owner.username


class AdvertisementResponsePermissions(SenyAuth):

    message = "Only the response owner or advertisement owner can access this."

    def has_object_permission(self, request, view, obj):
        if request.user.username == obj.owner.username:
            return True
        if request.user.username == obj.advertisement.product.owner.username:
            return True
        return False


class TagPermissions(SenyPermission):

    message = "Tags can not be edited or deleted."

    def has_permission(self, request, view):
        return request.method in ['POST', 'GET']


class ReviewPermissions(SenyPermission):

    message = "Only the owner of the review can modify/delete it."

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return obj.owner.username == request.user.username

