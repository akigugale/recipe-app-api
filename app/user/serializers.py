from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5, }}

    def create(self, validated_data):
        """Create a new user model with encrpted password and return it."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user profile with encrypted password and return it"""
        # if password isn't there its None
        password = validated_data.pop('password', None)
        # using super to use the default update function and extending it for
        # custom password (encrypted)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication obeject"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):  # ATTRS is dict of all seralizer fields
        """Validate and authenticate users"""
        email = attrs.get('email')
        passowrd = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=passowrd
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user

        return attrs
