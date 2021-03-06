from rest_framework import serializers

from rentlist.util import *
from rest_framework import serializers
from rentlist.models import *


class ImageSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username', read_only=True)

    class Meta:
        model = Image
        fields = ('id', 'owner', 'image', 'title')

    def create(self, validated_data):
        image = Image(**validated_data)
        image.owner = self.context['request'].user
        image.save()
        return image


class ImageForProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(source='products', queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = Image
        fields = ('id', 'image', 'title', 'product')

    def create(self, validated_data):
        product = validated_data.pop('products')
        image = Image(**validated_data)
        image.owner = self.context['request'].user
        image.save()
        image.products.add(product)
        product.images.add(image)
        return image


class AdvertisementResponseSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    advertisement_owner = serializers.ReadOnlyField(source='advertisement.product.owner.username')
    advertisement_title = serializers.ReadOnlyField(source='advertisement.product.title')

    class Meta:
        model = AdvertisementResponse
        fields = ('id', 'owner', 'advertisement', 'advertisement_owner', 'created_at', 'deadline', 'accepted', 'advertisement_title') #'reviewed'

    def create(self, validated_data):
        response = AdvertisementResponse(**validated_data)
        response.owner = self.context['request'].user
        response.save()
        return response


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ("text", "products")
        extra_kwargs = {}


class ReviewSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    product_id = serializers.PrimaryKeyRelatedField(source='product', queryset=Product.objects.all(), write_only=True)
    product_title = serializers.ReadOnlyField(source='product.title')
    product_owner = serializers.ReadOnlyField(source='product.owner.username')

    class Meta:
        model = Review
        fields = ("id", "owner", "rating", "title", "content", "created_at", "product_id", "product_title", "product_owner")
        extra_kwargs = {}

    def create(self, validated_data):
        user = self.context['request'].user
        review = Review(**validated_data)
        review.owner = user
        if user.username == review.product.owner.username:
            raise serializers.ValidationError("Cannot review your own product.")

        for r in review.product.reviews.all():
            if r.owner == review.owner:
                raise serializers.ValidationError("You have already reviewed this product.")
        review.save()
        return review


class ProductWithImageSerializer(serializers.ModelSerializer):
    display_image = ImageSerializer()
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True, source='owner')
    deposit = serializers.FloatField(default=0)
    tags = TagSerializer(many=True, read_only=True)
    rating = serializers.ReadOnlyField()
    images = ImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    can_review = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ("id", "price_metric", "price", "description", "title", "type", "owner", "owner_id", "display_image",
                  "deposit", "tags", 'tags', 'rating', 'images', 'reviews', 'can_review')
        extra_kwargs = {}

    def create(self, validated_data):
        image = validated_data.get('display_image', None)
        del validated_data['display_image']
        user = self.context['request'].user
        prod = Product(**validated_data)
        prod.owner = user
        prod.save()
        prod.collect_tags()
        if image:
            image = Image(**image)
            image.owner = user
            image.save()
            image.products_displaying_image.add(prod)
            image.products.add(prod)
            prod.images.add(image)
        return prod

    def get_can_review(self, obj):
        user = self.context['request'].user
        if not obj.has_reviewed(user):
            return len(AdvertisementResponse.objects.filter(advertisement__product_id=obj.pk, owner=user, accepted=1)) != 0
        return False


class ProductSerializer(serializers.ModelSerializer):
    rating = serializers.ReadOnlyField()
    tags = TagSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_id = serializers.PrimaryKeyRelatedField(read_only=True, source='owner')
    deposit = serializers.FloatField(default=0)
    display_image = serializers.PrimaryKeyRelatedField(queryset=Image.objects.all(), allow_null=True, default=None)
    can_review = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ("id", "price_metric", "price", "description", "title", "type", "owner", "owner_id", "tags", "rating", "images",
                  "reviews", "display_image", "deposit", 'can_review')
        extra_kwargs = {}

    def create(self, validated_data):
        user = self.context['request'].user
        prod = Product(**validated_data)
        prod.owner = user
        prod.save()
        prod.collect_tags()
        return prod

    def update(self, instance: Product, validated_data):
        image = validated_data.get('display_image', None)
        del validated_data['display_image']
        for key in validated_data.keys():
            setattr(instance, key, validated_data[key])
        instance.save()
        instance.collect_tags()
        if image:
            image.products_displaying_image.add(instance)
            image.save()
            image.products.add(instance)
            instance.images.add(image)
        return instance

    def get_can_review(self, obj):
        user = self.context['request'].user
        if not obj.has_reviewed(user):
            return len(AdvertisementResponse.objects.filter(advertisement__product_id=obj.pk, owner=user, accepted=1)) != 0
        return False




class UserProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    supply_reviews = serializers.SerializerMethodField()
    demand_reviews = serializers.SerializerMethodField()
    supply_rating = serializers.ReadOnlyField(source="average_supply_rating")
    demand_rating = serializers.ReadOnlyField(source="average_demand_rating")
    owner_id = serializers.ReadOnlyField(source="owner.id")
    profile_type = serializers.ReadOnlyField()
    lat = serializers.FloatField(allow_null=True)
    long = serializers.FloatField(allow_null=True)
    email = serializers.ReadOnlyField(source='owner.email', allow_null=True)

    class Meta:
        model = UserProfile
        fields = ("id", "zip", "title", "description", "owner", "owner_id", "email", "lat", "long", "profile_type",
                  "supply_reviews", "demand_reviews", "supply_rating", "demand_rating")
        extra_kwargs = {"profile_type": {"read_only": True}}

    def update(self, instance, validated_data):
        for key in validated_data.keys():
            setattr(instance, key, validated_data[key])
        lat, long = validated_data.get('lat', None), validated_data.get('long', None)
        if not lat or not long:
            instance.lat, instance.long = get_geo(instance.zip)
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
        serializer = ReviewSerializer(many=True, data=obj.get_supply_reviews()[0:5])
        serializer.is_valid()
        return serializer.data

    def get_demand_reviews(self, obj):
        serializer = ReviewSerializer(many=True, data=obj.get_demand_reviews()[0:5])
        serializer.is_valid()
        return serializer.data


class MessageSerializer(serializers.ModelSerializer):
    images = ImageSerializer(read_only=True, many=True)
    destination = serializers.ReadOnlyField(source='destination.username')
    destination_id = serializers.PrimaryKeyRelatedField(source='destination', read_only=True)
    source = serializers.ReadOnlyField(source='source.username')
    source_id = serializers.PrimaryKeyRelatedField(source='source', read_only=True)
    thread = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=MessageThread.objects.all())
    response = AdvertisementResponseSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Message
        fields = ('id', 'created_at', 'thread', 'destination', 'destination_id', 'source', 'source_id',
                  'content', 'new', 'images', 'response')
        extra_kwargs = {'new': {'read_only': True}, 'created_at': {'read_only': True}}

    def create(self, validated_data):
        message = Message(**validated_data)
        user = self.context['request'].user
        if user == message.thread.creator:
            message.destination = message.thread.responder
        else:
            message.destination = message.thread.creator
        message.source = user
        if self.validUsers(user.username, message):
            message.save()
            message.thread.updated_at = datetime.now()
            message.thread.save()
            return message
        raise serializers.ValidationError('Messages can only be created by users active on thread.')

    def validUsers(self, user, message):
        return (user == message.thread.creator.username and message.destination.username == message.thread.responder.username) or\
               (user == message.thread.responder.username and message.destination.username == message.thread.creator.username)


class MessageWithThreadSerializer(serializers.ModelSerializer):
    thread_title = serializers.CharField(write_only=True)

    class Meta:
        model = Message
        fields = ('destination',
                  'content', 'thread_title') # 'image_id',

    def create(self, validated_data):
        user = self.context['request'].user
        thread = validated_data['thread_title']
        del validated_data['thread_title']
        thread = MessageThread(creator=user, responder=validated_data['destination'], title=thread)
        thread.save()
        message = Message(**validated_data)
        message.thread = thread
        message.source = user
        if self.validUsers(user.username, message):
            message.save()
            return message
        raise serializers.ValidationError('Messages can only be created by users active on thread.')

    def validUsers(self, user, message):
        return (user == message.thread.creator.username and message.destination.username == message.thread.responder.username) or\
               (user == message.thread.responder.username and message.destination.username == message.thread.creator.username)


class MessageWithThreadAndResponseSerializer(serializers.ModelSerializer):
    thread_title = serializers.CharField(write_only=True)
    advertisement = serializers.IntegerField(write_only=True)
    deadline = serializers.DateTimeField(write_only=True)
    accepted = serializers.BooleanField(write_only=True)

    class Meta:
        model = Message
        fields = ('destination',
                  'content', 'thread_title', 'advertisement', 'deadline', 'accepted') # 'image_id',

    def create(self, validated_data):
        user = self.context['request'].user
        thread = validated_data['thread_title']
        del validated_data['thread_title']
        thread = MessageThread(creator=user, responder=validated_data['destination'], title=thread)
        ad = Advertisement.objects.get(pk=validated_data['advertisement'])
        response = AdvertisementResponse(owner=user, advertisement=ad,
                                         deadline=validated_data['deadline'], accepted=validated_data['accepted'])
        del validated_data['advertisement']
        del validated_data['deadline']
        del validated_data['accepted']
        message = Message(**validated_data)
        message.source = user
        try:
            thread.save()
            message.thread = thread
            if self.validUsers(user.username, message):
                response.save()
                message.response = response
                message.save()
                return message
            raise serializers.ValidationError('Messages can only be created by users active on thread.')
        except:
            if thread.pk:
                thread.delete()
            if response.pk:
                response.delete()
            if message.pk:
                message.delete()
                raise serializers.ValidationError('Something went wrong creating this message.')

    def validUsers(self, user, message):
        return (user == message.thread.creator.username and message.destination.username == message.thread.responder.username) or\
               (user == message.thread.responder.username and message.destination.username == message.thread.creator.username)


class MessageThreadSerializer(serializers.ModelSerializer):
    new_messages = serializers.ReadOnlyField()
    messages = MessageSerializer(many=True, read_only=True)
    creator = serializers.ReadOnlyField(source='creator.username')
    responder = serializers.ReadOnlyField(source='responder.username')
    creator_id = serializers.PrimaryKeyRelatedField(source='creator', queryset=User.objects.all())
    responder_id = serializers.PrimaryKeyRelatedField(source='responder', queryset=User.objects.all())

    class Meta:
        model = MessageThread
        fields = ("id", "created_at", "creator", "creator_id", "responder", "responder_id", "title", "messages", 'new_messages')
        extra_kwargs = {}


class AdvertisementSerializer(serializers.ModelSerializer):
    product = ProductWithImageSerializer(read_only=True)
    responses = AdvertisementResponseSerializer(many=True, read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Product.objects.all())
    distance = serializers.FloatField(read_only=True)
    owner = serializers.ReadOnlyField(source='product.owner.username')
    lat = serializers.FloatField(allow_null=True)
    lon = serializers.FloatField(allow_null=True)
    accepted = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = ('id', 'owner', 'start', 'end', 'active', 'zip', 'lat', 'lon', 'responses', 'product', 'product_id', 'distance', 'accepted')
        extra_kwargs = {}

    def create(self, validated_data):
        ad = Advertisement(**validated_data)
        product_id = validated_data['product_id'].id
        del validated_data['product_id']
        if not validated_data.get('lat', False) and not validated_data.get('lon', False):
            ad.lat, ad.lon = get_geo(ad.zip)
        ad.product_id = product_id
        if ad.start > ad.end:
            raise serializers.ValidationError("Start must be before end.")
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
        if instance.start > instance.end:
            raise serializers.ValidationError("Start must be before end.")
        instance.save()
        return instance

    def get_accepted(self, obj):
        return obj.accepted()


class SignUpSerializer(serializers.ModelSerializer):
    client_id = serializers.SerializerMethodField()
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'client_id', 'client_secret')
        write_only_fields = ('password',)

    def get_client_id(self, obj):
        return obj.application_set.first().client_id

    def get_client_secret(self, obj):
        return obj.application_set.first().client_secret

    def create(self, validated_data):
        user = User(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(SignUpSerializer):
    class Meta:
        model = User
        fields = ('client_id', 'client_secret')