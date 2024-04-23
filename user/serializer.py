from rest_framework import serializers
from .models import User


class UserDataSerial(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "get_image",
            "phone",
            "address",
            "is_verified",
        ]

