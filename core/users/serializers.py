from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
            'email': {
                'validators': [UniqueValidator(queryset=User.objects.all())],
            },  
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required for updates
        if self.instance is not None:
            self.fields['username'].required = False
            self.fields['email'].required = False
            self.fields['role'].required = False
            self.fields['password'].required = False

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('groups', None)
        validated_data.pop('user_permissions', None)
        password = validated_data.pop('password', None)
        profile_picture = validated_data.pop('profile_picture', None)

        # Handle partial updates - only update provided fields
        for attr, value in validated_data.items():
            if value is not None or attr in ['profile_picture']:  # Special handling for file fields
                setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        if profile_picture is not None:  # Explicit None check for file fields
            instance.profile_picture = profile_picture

        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            # Fetch the user by email
            user = get_user_model().objects.get(email=data['email'])
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError('Incorrect credentials')
        
        # Check if the password matches
        if not user.check_password(data['password']):
            raise serializers.ValidationError('Incorrect credentials')

        if user and user.is_active:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            print("refresh:",refresh)
            print("access:",refresh.access_token)
            return {
                'username': user.username,
                'email': user.email,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }

        raise serializers.ValidationError('Incorrect credentials')


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)