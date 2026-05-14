from rest_framework import viewsets, permissions, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from openai import OpenAI
from django.conf import settings
from .models import Subscription
from .serializers import SubscriptionSerializer
from rest_framework.decorators import action
from .permissions import IsAdminUserOnly
import traceback

from .models import (
    Client,
    Program,
    Workout,
    Exercise,
    WorkoutExercise,
    Appointment,
    ClientProgress,
    ExerciseProgress,
)

from .serializers import (
    TrainerSignupSerializer,
    RegisterSerializer,
    ClientSerializer,
    ProgramSerializer,
    WorkoutSerializer,
    ExerciseSerializer,
    WorkoutExerciseSerializer,
    AppointmentSerializer,
    ClientProgressSerializer,
    ExerciseProgressSerializer,
)


class IsTrainer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class TrainerSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TrainerSignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Trainer account created"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsTrainer]

    def get_queryset(self):
        return Client.objects.filter(trainer=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsTrainer]

    def get_queryset(self):
        return Program.objects.filter(trainer=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)


class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [IsTrainer]

    def get_queryset(self):
        queryset = Workout.objects.filter(program__trainer=self.request.user)

        program_id = self.request.query_params.get("program")

        if program_id:
            queryset = queryset.filter(program_id=program_id)

        return queryset


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsTrainer]


class WorkoutExerciseViewSet(viewsets.ModelViewSet):
    queryset = WorkoutExercise.objects.all()
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [IsTrainer]

    def get_queryset(self):
        return WorkoutExercise.objects.filter(
            workout__program__trainer=self.request.user
        )


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsTrainer]

    def get_queryset(self):
        return Appointment.objects.filter(trainer=self.request.user).order_by(
            "appointment_date", "appointment_time"
        )

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)


class ClientProgressViewSet(viewsets.ModelViewSet):
    queryset = ClientProgress.objects.all()
    serializer_class = ClientProgressSerializer
    permission_classes = [IsTrainer]

    def get_queryset(self):
        queryset = ClientProgress.objects.filter(trainer=self.request.user).order_by(
            "-recorded_at"
        )

        client_id = self.request.query_params.get("client")

        if client_id:
            queryset = queryset.filter(client_id=client_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)


class ExerciseProgressViewSet(viewsets.ModelViewSet):
    queryset = ExerciseProgress.objects.all()
    serializer_class = ExerciseProgressSerializer
    permission_classes = [IsTrainer]

    def get_queryset(self):
        queryset = ExerciseProgress.objects.filter(trainer=self.request.user).order_by(
            "-recorded_at"
        )

        client_id = self.request.query_params.get("client")
        exercise_id = self.request.query_params.get("exercise")

        if client_id:
            queryset = queryset.filter(client_id=client_id)

        if exercise_id:
            queryset = queryset.filter(exercise_id=exercise_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)


class AITrainingPlanView(APIView):
    permission_classes = [IsTrainer]

    def post(self, request):
        try:
            goal = request.data.get("goal", "")
            experience = request.data.get("experience", "")
            limitations = request.data.get("limitations", "")
            focus = request.data.get("focus", "")

            if not settings.OPENAI_API_KEY:
                return Response(
                    {"error": "OPENAI_API_KEY is not configured."},
                    status=500
                )

            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            prompt = f"""
            Create a safe personal training plan.

            Goal: {goal}
            Experience: {experience}
            Limitations: {limitations}
            Focus: {focus}

            Include:
            - workouts
            - exercises
            - sets
            - reps
            - rest times
            - trainer notes

            Responsible AI rules:
            - Do not provide medical diagnosis.
            - Mention trainer review is required.
            - Avoid unsafe extreme advice.
            """

            response = client.responses.create(
                model="gpt-5.4-mini",
                input=prompt,
            )

            return Response({
                "suggestion": response.output_text
            })

        except Exception as e:
            print("AI TRAINING PLAN ERROR:")
            print(str(e))
            traceback.print_exc()

            return Response(
                {"error": str(e)},
                status=500
            )


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAdminUserOnly]

    @action(detail=True, methods=["patch"])
    def archive(self, request, pk=None):
        subscription = self.get_object()
        subscription.is_archived = True
        subscription.status = "archived"
        subscription.save()

        return Response({"message": "Subscription archived"})


class MeView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "is_staff": request.user.is_staff,
                "is_superuser": request.user.is_superuser,
            }
        )
