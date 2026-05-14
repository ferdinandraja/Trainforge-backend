from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import User
class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('trainer', 'Trainer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')


class TrainerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=255)

    specialization = models.CharField(
        max_length=255
    )

    experience_years = models.IntegerField(
        default=0
    )

    bio = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.full_name
class Client(models.Model):
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_clients"
    )
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    goal = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Program(models.Model):
    trainer = models.ForeignKey(User,on_delete=models.CASCADE)
    preferred_appointment_times = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(
    Client,
    on_delete=models.CASCADE
)
    def __str__(self):
        return self.title

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()

class Workout(models.Model):
    program = models.ForeignKey(Program,on_delete=models.CASCADE,related_name="workouts")
    name = models.CharField(max_length=255)
    day = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout,on_delete=models.CASCADE,related_name="workout_exercises")
    exercise = models.ForeignKey(Exercise,on_delete=models.CASCADE)
    sets = models.IntegerField()
    reps = models.IntegerField()
    rest_seconds = models.IntegerField(default=60)
    notes = models.TextField(blank=True)
    def __str__(self):
        return (
            f"{self.exercise.name} - "
            f"{self.sets}x{self.reps}"
        )

class TrainerClient(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trainer')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client')

class Appointment(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ClientProgress(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    weight_kg = models.FloatField()
    body_fat_percentage = models.FloatField(null=True, blank=True)
    muscle_mass_kg = models.FloatField(null=True, blank=True)

    progress_notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.full_name} progress"
    

class ExerciseProgress(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    weight_used_kg = models.FloatField(null=True, blank=True)
    sets_completed = models.IntegerField()
    reps_completed = models.IntegerField()

    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.full_name} - {self.exercise.name}"
    
class Subscription(models.Model):
    PLAN_CHOICES = (
        ("starter", "Starter"),
        ("professional", "Professional"),
        ("enterprise", "Enterprise"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
        ("archived", "Archived"),
    )

    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    plan_name = models.CharField(
        max_length=50,
        choices=PLAN_CHOICES
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="active"
    )

    monthly_price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def archive(self):
        self.is_archived = True
        self.status = "archived"
        self.save()

    def __str__(self):
        return f"{self.trainer.username} - {self.plan_name}"