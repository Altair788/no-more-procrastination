from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def create(self, validated_data):
        email = validated_data.get("email")

        # Проверка на существование пользователя с таким же именем
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": ["Пользователь с такой почтой уже существует."]}
            )

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
        )

        read_only_fields = ("id",)
