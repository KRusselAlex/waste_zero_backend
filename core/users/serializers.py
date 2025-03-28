from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'validators': [UniqueValidator(queryset=User.objects.all())]}  # Ensure email is unique
        }
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Hash the password before saving
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