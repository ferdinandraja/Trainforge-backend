from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'role']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class WorkoutExerciseSerializer(
    serializers.ModelSerializer
):
    exercise_name = serializers.CharField(
        source="exercise.name",
        read_only=True
    )
    exercise_description = serializers.CharField(
        source="exercise.description",
        read_only=True
    )
    class Meta:
        model = WorkoutExercise
        fields = [
            "id",
            "workout",
            "exercise",
            "exercise_name",
            "exercise_description",
            "sets",
            "reps",
            "rest_seconds",
            "notes",
        ]
        
class WorkoutSerializer(serializers.ModelSerializer):
    workout_exercises = WorkoutExerciseSerializer(
            many=True,
            read_only=True
        )

    class Meta:
        model = Workout

        fields = "__all__"

class ProgramSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.full_name",
        read_only=True
    )

    client_age = serializers.IntegerField(
        source="client.age",
        read_only=True
    )

    client_goal = serializers.CharField(
        source="client.goal",
        read_only=True
    )

    class Meta:
        model = Program
        fields = "__all__"
        read_only_fields = [
            "trainer",
            "created_at",
            "client_name",
            "client_age",
            "client_goal",
        ]

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'





class TrainerClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerClient
        fields = '__all__'


class TrainerSignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    full_name = serializers.CharField()
    specialization = serializers.CharField()

    experience_years = serializers.IntegerField()

    bio = serializers.CharField(required=False)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        TrainerProfile.objects.create(
            user=user,
            full_name=validated_data["full_name"],
            specialization=validated_data["specialization"],
            experience_years=validated_data[
                "experience_years"
            ],
            bio=validated_data.get("bio", "")
        )

        return user
    
class AppointmentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.full_name",
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ["trainer", "created_at", "client_name"]

    def validate(self, data):
        request = self.context.get("request")
        trainer = request.user

        appointment_date = data["appointment_date"]
        appointment_time = data["appointment_time"]
        duration_minutes = data.get("duration_minutes", 60)

        new_start = datetime.combine(appointment_date, appointment_time)
        new_end = new_start + timedelta(minutes=duration_minutes)

        existing_appointments = Appointment.objects.filter(
            trainer=trainer,
            appointment_date=appointment_date
        )

        for appointment in existing_appointments:
            existing_start = datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )

            existing_end = existing_start + timedelta(
                minutes=appointment.duration_minutes
            )

            if new_start < existing_end and new_end > existing_start:
                raise serializers.ValidationError(
                    "This appointment time overlaps with another client appointment."
                )

        return data
    
class ClientProgressSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.full_name",
        read_only=True
    )

    class Meta:
        model = ClientProgress
        fields = "__all__"
        read_only_fields = ["trainer", "recorded_at", "client_name"]

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ["trainer", "created_at"]

class ExerciseProgressSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    program_title = serializers.CharField(source="program.title", read_only=True)
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)

    class Meta:
        model = ExerciseProgress
        fields = "__all__"
        read_only_fields = [
            "trainer",
            "recorded_at",
            "client_name",
            "program_title",
            "exercise_name",
        ]

class SubscriptionSerializer(serializers.ModelSerializer):
    trainer_username = serializers.CharField(
        source="trainer.username",
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = "__all__"