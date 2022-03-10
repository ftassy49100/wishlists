from .models import *
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework import serializers

class UserAdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    firstname = serializers.CharField(
        required=True,
    )

    lastname = serializers.CharField(
        required=True,
    )

    password = serializers.CharField(min_length=3, write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'], 
        firstname=validated_data['firstname'], lastname=validated_data['lastname'])
        return user


    class Meta:
        model = User
        fields = ['id', 'username', 'firstname', 'lastname', 'email', 'password']

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class IdeaAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = '__all__'     


class WishlistAdminSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserAdminSerializer(many=False)
    contributors = UserAdminSerializer(many=True)
    idea_set = IdeaAdminSerializer(many=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'name', 'creation_date', 'creator', 'contributors', 'idea_set', 'is_active']