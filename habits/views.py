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


#  Кастомный эндпоинт для публичных привычек
class PublicHabitListApiView(ListAPIView):
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    pagination_class = HabitPaginator
    permission_classes = [AllowAny]
