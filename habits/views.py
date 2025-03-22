from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from habits.models import Habit
from habits.paginations import HabitPaginator
from habits.serializers import HabitSerializer


class HabitViewSet(ModelViewSet):
    """
    Представление для работы с привычками текущего пользователя.
    """

    serializer_class = HabitSerializer
    pagination_class = HabitPaginator
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Получить список привычек текущего пользователя",
        responses={200: HabitSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Создать новую привычку",
        request=HabitSerializer,
        responses={201: HabitSerializer()}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Получить детальную информацию о привычке",
        responses={200: HabitSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Обновить существующую привычку",
        request=HabitSerializer,
        responses={200: HabitSerializer()}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить привычку",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        Возвращает привычки, принадлежащие текущему пользователю.
        """
        return Habit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Устанавливает текущего пользователя как владельца привычки.
        """
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        Запрещает редактирование публичных привычек.
        """
        if self.get_object().is_public:
            raise PermissionDenied("Вы не можете редактировать публичную привычку.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Запрещает удаление публичных привычек.
        """
        if instance.is_public:
            raise PermissionDenied("Вы не можете удалять публичную привычку.")
        instance.delete()


@extend_schema(
    description="API endpoint для просмотра публичных привычек.",
    responses={200: HabitSerializer(many=True)}
)

#  Кастомный эндпоинт для публичных привычек
class PublicHabitListApiView(ListAPIView):
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    pagination_class = HabitPaginator
    permission_classes = [AllowAny]
