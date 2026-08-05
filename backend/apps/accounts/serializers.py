from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User as UserModel
from .services import verify_otp

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT token serializer with extra user claims."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['is_email_verified'] = user.is_email_verified
        return token


class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password2', 'referral_code']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        validated_data.pop('password2')
        password = validated_data.pop('password')

        user = User(**validated_data)

        # Link parent via referral code
        if referral_code:
            try:
                parent = User.objects.get(referral_code=referral_code)
                user.parent = parent
            except User.DoesNotExist:
                raise serializers.ValidationError({'referral_code': 'Invalid referral code.'})

        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Read/write user profile details."""

    full_name = serializers.SerializerMethodField(read_only=True)
    parent_email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'country', 'profile_picture',
            'role', 'kyc_status', 'is_email_verified', 'is_2fa_enabled',
            'referral_code', 'parent_email', 'active_level',
            'date_joined', 'created_at',
        ]
        read_only_fields = [
            'id', 'email', 'role', 'kyc_status', 'is_email_verified',
            'referral_code', 'active_level', 'date_joined', 'created_at', 'parent_email',
        ]

    def get_full_name(self, obj) -> str:
        return obj.full_name

    def get_parent_email(self, obj) -> str | None:
        return obj.parent.email if obj.parent else None


class ChangePasswordSerializer(serializers.Serializer):
    """Change password (requires old password)."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True, label='Confirm New Password')

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': "Passwords do not match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """Send OTP to email for password reset."""

    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password using OTP."""

    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, label='Confirm New Password')

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': "Passwords do not match."})
        return attrs


class VerifyEmailSerializer(serializers.Serializer):
    """Verify email address using OTP."""

    otp = serializers.CharField(required=True, max_length=6)


class ResendOTPSerializer(serializers.Serializer):
    """Request a new OTP for email verification."""

    email = serializers.EmailField(required=True)
