from rentlist.util import *
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from oauth2_provider.models import Application
from collections import namedtuple

"""Application Models"""


PROFILE_TYPES_ENUM = {"free": 0, "premium": 2}
PROFILE_TYPES = ((PROFILE_TYPES_ENUM[key], key) for key in PROFILE_TYPES_ENUM.keys())
PRODUCT_TYPES_ENUM = {"supply": 0, "demand": 2}
PRODUCT_TYPES = ((PRODUCT_TYPES_ENUM[key], key) for key in PRODUCT_TYPES_ENUM.keys())
METRIC_TYPES_ENUM = {'hourly': 0, 'daily': 2, 'weekly': 4, 'monthly': 8}
METRIC_TYPES = ((METRIC_TYPES_ENUM[key], key) for key in METRIC_TYPES_ENUM.keys())


class Tag(models.Model):
    text = models.CharField(max_length=20, unique=True)


class Image(models.Model):
    image = models.ImageField()
    title = models.TextField(default='')
    owner = models.ForeignKey(User, related_name='images')

    def __str__(self):
        return self.title


class Product(models.Model):
    price_metric = models.IntegerField(default=0, choices=METRIC_TYPES)
    price = models.FloatField(default=0)
    description = models.TextField(default='')
    title = models.TextField(default='')
    type = models.IntegerField(default=0, choices=PRODUCT_TYPES)
    owner = models.ForeignKey(User, related_name='products')
    tags = models.ManyToManyField(Tag, related_name='products')
    images = models.ManyToManyField(Image, related_name='products', blank=True)
    display_image = models.ForeignKey(Image, related_name='products_displaying_image', null=True, blank=True)
    deposit = models.FloatField(default=0)

    def __str__(self):
        return self.title

    def rating(self):
        if len(self.reviews.all()):
            return sum([review.rating for review in self.reviews.all()])/len(self.reviews.all())
        return 0

    def collect_tags(self):
        tags = {tag.strip('#') for tag in self.description.split() if tag.startswith('#') and len(tag) < 20}
        for tag in tags:
            _tag = Tag.objects.filter(text=tag)
            if _tag.count():
                self.tags.add(_tag[0])
            else:
                self.tags.create(text=tag)
        self.save()

    def has_reviewed(self, username):
        return any(review.product.owner == username for review in self.reviews.all())


class UserProfile(models.Model):
    zip = models.CharField(max_length=5)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, related_name='profile')
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    profile_type = models.IntegerField(default=0, choices=PROFILE_TYPES)

    def average_demand_rating(self):
        reviews = self.get_demand_reviews()
        if reviews:
            return sum(review.rating for review in reviews)/len(reviews)
        return 'n/a'

    def average_supply_rating(self):
        reviews = self.get_supply_reviews()
        if reviews:
            return sum(review.rating for review in reviews)/len(reviews)
        return 'n/a'

    def get_supply_reviews(self):
        return Review.objects.filter(product__owner=self.owner, product__type=0)

    def get_demand_reviews(self):
        return Review.objects.filter(product__type=2, product__owner=self.owner)

    def __str__(self):
        return self.owner.username
    # todo: images


class Advertisement(models.Model):
    product = models.ForeignKey(Product, related_name='advertisements')
    start = models.DateTimeField(default=datetime.now())
    end = models.DateTimeField(default=datetime.now())
    active = models.BooleanField(default='1')
    zip = models.CharField(max_length=5, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    distance = None

    def __str__(self):
        return self.product.title + " {0}".format(str(self.start))
    # todo: images

    class Meta:
        ordering = ("-start", "-end")

    def accepted(self):
        for response in self.responses.all():
            if response.accepted:
                return True
        return False


class Review(models.Model):
    owner = models.ForeignKey(User, related_name="reviews")
    product = models.ForeignKey(Product, related_name="reviews")
    rating = IntegerRangeField(min_value=0, max_value=5, default=3)
    title = models.TextField(default='')
    content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True, default=datetime.now())

    class Meta:
        ordering = ('-created_at',)


class AdvertisementResponse(models.Model):
    owner = models.ForeignKey(User, related_name='responses')
    advertisement = models.ForeignKey(Advertisement, related_name='responses')
    created_at = models.DateTimeField(auto_now_add=True, default=datetime.now())
    deadline = models.DateTimeField(blank=True)
    accepted = models.BooleanField(default=False)

    def type(self):
        return self.advertisement.product.type

    class Meta:
        ordering = ('-created_at',)


class MessageThread(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated_at = models.DateTimeField(auto_now_add=True, default=datetime.now())
    creator = models.ForeignKey(User, related_name='threads')
    responder = models.ForeignKey(User, related_name='incoming_threads')
    title = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def new_messages(self):
        return len([message for message in self.messages.all() if message.new])

    class Meta:
        ordering = ('-updated_at',)


class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, default=datetime.now())
    thread = models.ForeignKey(MessageThread, related_name='messages')
    destination = models.ForeignKey(User, related_name='incoming_messages')
    source = models.ForeignKey(User, related_name='messages')
    content = models.TextField(blank=True)
    new = models.BooleanField(default=True)
    images = models.ManyToManyField(Image, related_name='messages', blank=True)
    response = models.ForeignKey(AdvertisementResponse, related_name='response', blank=True, null=True);

    class Meta:
        ordering = ('created_at',)





# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)

def create_auth_client_and_profile(sender, instance=None, created=False, **kwargs):
    """
    Intended to be used as a receiver function for a `post_save` signal
    on a custom User model
    Creates client_id and client_secret for authenticated users
    """
    if created:
        profile = UserProfile(owner=instance)
        profile.save()
        Application.objects.create(user=instance,
                                   client_type=Application.CLIENT_CONFIDENTIAL,
                                   authorization_grant_type=Application.GRANT_PASSWORD)



post_save.connect(create_auth_client_and_profile, sender=User)

