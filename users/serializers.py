import secrets

from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели User.
    """

    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    id = serializers.IntegerField(read_only=True)
    token = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    tg_id = serializers.IntegerField(allow_null=True, required=False)
    tg_nick = serializers.CharField(allow_null=True, required=False)
    phone = serializers.CharField(allow_null=True, required=False)
    avatar = serializers.ImageField(
        allow_null=True,  # Поле может быть пустым
        required=False,  # Необязательно для заполнения
        use_url=True  # Возвращать полный URL (если настроен MEDIA_URL)
    )

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
        user.is_active = False  # Пользователь не активен до подтверждения email
        user.token = secrets.token_hex(16)  # Генерация токена для подтверждения email
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            "id",  # Только для чтения
            "email",  # Обязателен для заполнения
            "password",  # Только для записи
            "tg_id",  # Не обязателен для заполнения
            "tg_nick",  # Не обязателен для заполнения
            "phone",  # Не обязателен для заполнения
            "country",  # Не обязателен для заполнения
            "avatar",  # Не обязателен для заполнения
            "is_active",  # Только для чтения
            "token",  # Только для чтения
        )


class PasswordResetSerializer(serializers.Serializer):
    """
    Сериализатор для отправки email на сброс пароля
    Этот сериализатор проверяет, существует ли пользователь с указанным email,
    и генерирует токен для сброса пароля
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        user.token = secrets.token_hex(16)  # Генерация токена для сброса пароля
        user.save()
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля
    Этот сериализатор принимает токен и новый пароль,
    проверяет их и обновляет пароль пользователя
    """
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not User.objects.filter(token=data["token"]).exists():
            raise serializers.ValidationError("Неверный токен.")
        return data

    def save(self):
        user = User.objects.get(token=self.validated_data["token"])
        user.set_password(self.validated_data["new_password"])
        user.token = None  # Удаляем токен после успешного сброса пароля
        user.save()
