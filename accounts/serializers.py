from rest_framework import serializers
from django.contrib.auth import get_user_model

# WHY get_user_model() and not import User directly?
# get_user_model() always returns whatever AUTH_USER_MODEL is set to.
# If you import User directly and someone swaps the model, your code breaks.
# get_user_model() = future-proof.
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer = a blueprint for what data is accepted/returned via the API.
    ModelSerializer auto-generates fields from your Model — less code.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
        # write_only=True means: accept this field on input, but NEVER send it back in responses.
        # You never want to return a password in JSON, even hashed.
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_seller']
        # Only these fields are exposed. 'id' is read-only by default.

    def create(self, validated_data):
        # WHY override create()?
        # ModelSerializer's default create() calls User.objects.create(**data)
        # which stores the password as PLAIN TEXT. We must use create_user()
        # which hashes the password using Django's PBKDF2 algorithm.
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Used to return user profile data — no password field."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_seller']
        read_only_fields = ['id', 'email']
        # read_only_fields = these can be returned but never changed via this serializer