from rest_framework import serializers

from rentlist.util import *
from rest_framework import serializers
from rentlist.models import *




#
# class ReviewSerializer(serializers.HyperlinkedModelSerializer):
#
#     class Meta:
#         model = Review
#         fields = ("url", "supplier", "demander", "advertisement", "rating", "title", "content")
#
#     def create(self, validated_data):
#         review = Review(**validated_data)
#         if review.advertisement.type == 'd->s':
#             review.source = review.demander.owner
#             review.destination = review.supplier.owner
#         else:
#             review.source = review.supplier.owner
#             review.destination = review.demander.owner
#         review.save()
#         return review

# serializers
class ImageSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Image
        fields = ('id', 'owner', 'image', 'title')

    def create(self, validated_data):
        image = Image(**validated_data)
        image.owner = self.context['request'].user
        image.save()
        return image



class AdvertisementResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdvertisementResponse
        fields = ('owner', 'advertisement', 'created_at', 'deadline', 'accepted', 'reviewed')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ("text", "products")
        extra_kwargs = {}


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ("owner", "product", "rating", "title", "content", "created_at")
        extra_kwargs = {}


class ExistingImageProductCreateSerializer(serializers.ModelSerializer):
    rating = serializers.ReadOnlyField()
    tags = TagSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ("id", "price_metric", "price", "description", "title", "type", "owner", "tags", "rating", "images",
                  "reviews", "display_image")
        extra_kwargs = {}

class ProductSerializer(serializers.ModelSerializer):
    rating = serializers.ReadOnlyField()
    tags = TagSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    display_image = ImageSerializer()


    class Meta:
        model = Product
        fields = ("id", "price_metric", "price", "description", "title", "type", "owner", "tags", "rating", "images",
                  "reviews", "display_image")
        extra_kwargs = {}

    def create(self, validated_data):
        image_ref = validated_data.get('display_image_ref', None)
        del validated_data['display_image_ref']
        image = validated_data.get('display_image', None)
        del validated_data['display_image']
        prod = Product(**validated_data)
        prod.save()
        prod.collect_tags()
        if image:
            if image_ref:
                image = Image.objects.filter(id=image_ref)
            else:
                image = Image(**image)
                image.save()
            image.products_displaying_image.add(prod)
            image.products.add(prod)
        return prod

    def update(self, instance: Product, validated_data):
        image = validated_data.get('display_image', None)
        del validated_data['display_image']
        for key in validated_data.keys():
            setattr(instance, key, validated_data[key])
        instance.save()
        instance.collect_tags()
        if image:
            image = Image(**image)
            image.products_displaying_image.add(instance)
            image.save()
            image.products.add(instance)

        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    supply_reviews = serializers.SerializerMethodField()
    demand_reviews = serializers.SerializerMethodField()
    supply_rating = serializers.ReadOnlyField(source="average_supply_rating")
    demand_rating = serializers.ReadOnlyField(source="average_demand_rating")
    owner_id = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = UserProfile
        fields = ("zip", "title", "description", "owner", "owner_id", "lat", "long", "profile_type",
                  "supply_reviews", "demand_reviews", "supply_rating", "demand_rating")
        extra_kwargs = {"profile_type": {"read_only": True}}

    def update(self, instance, validated_data):
        zip_code = validated_data.get('zip', None)
        if zip_code:
            instance.lat, instance.long = get_geo(validated_data['zip'])
        for key in validated_data.keys():
            setattr(instance, key, validated_data[key])
        instance.save()
        return instance

    def create(self, validated_data):
        profile = UserProfile(**validated_data)
        lat, long = validated_data.get('lat', None), validated_data.get('long', None)
        if not lat or not long:
            profile.lat, profile.long = get_geo(profile.zip)
        profile.save()
        return profile

    def get_supply_reviews(self, obj):
        serializer = ReviewSerializer(many=True, data=obj.get_supply_reviews())
        serializer.is_valid()
        return serializer.data

    def get_demand_reviews(self, obj):
        serializer = ReviewSerializer(many=True, data=obj.get_demand_reviews())
        serializer.is_valid()
        return serializer.data


class MessageSerializer(serializers.ModelSerializer):
    images = ImageSerializer(read_only=True, many=True)

    class Meta:
        model = Message
        fields = ('id', 'created_at', 'thread', 'destination', 'source', 'content', 'new', 'images')
        extra_kwargs = {'is_new': {'read_only': True}, 'created_at': {'read_only': True}}


class MessageThreadSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = MessageThread
        fields = ("created_at", "creator", "responder", "title", "messages")
        extra_kwargs = {}


class AdvertisementSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    responses = AdvertisementResponseSerializer(many=True, read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Product.objects.all())
    distance = serializers.FloatField(read_only=True)

    class Meta:
        model = Advertisement
        fields = ('id', 'start', 'end', 'active', 'zip', 'lat', 'lon', 'responses', 'product', 'product_id', 'distance')
        extra_kwargs = {}

    def create(self, validated_data):
        ad = Advertisement(**validated_data)
        product_id = validated_data['product_id'].id
        del validated_data['product_id']
        if not validated_data.get('lat', False) and not validated_data.get('lon', False):
            ad.lat, ad.lon = get_geo(ad.zip)
        ad.product_id = product_id
        ad.save()
        return ad

    def update(self, instance: Advertisement, validated_data):
        product_id = validated_data.get('product_id', None)
        if product_id:
            instance.product_id = product_id.id
        del validated_data['product_id']
        if not validated_data.get('lat', False) and not validated_data.get('lon', False):
            if instance.zip != validated_data.get('zip', False):
                instance.lat, instance.lon = get_geo(validated_data.get('zip'))
        for key in validated_data.keys():
            setattr(instance, key, validated_data[key])
        instance.save()
        return instance


#
#
# class AdvertisementResponseSerializer(serializers.HyperlinkedModelSerializer):
#
#     class Meta:
#         model = AdvertisementResponse
#         fields = ("url",'supplier', 'demander', 'advertisement', 'accepted', 'acceptance_deadline', 'type')
#
#     def create(self, validated_data):
#         response = AdvertisementResponse(**validated_data)
#         if response.advertisement.type == 'd->s':
#             response.source = response.demander.owner
#             response.destination = response.supplier.owner
#         else:
#             response.source = response.supplier.owner
#             response.destination = response.demander.owner
#         response.save()
#         return response



#
#



class SignUpSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'password', 'client_id', 'client_secret')
        write_only_fields = ('password',)

    def get_client_id(self, obj):
        return obj.application_set.first().client_id

    def get_client_secret(self, obj):
        return obj.application_set.first().client_secret

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user



class LoginSerializer(SignUpSerializer):
    class Meta:
        model = User
        fields = ('client_id', 'client_secret')


