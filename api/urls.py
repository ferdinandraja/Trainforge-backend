from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView 

router = DefaultRouter()
router.register('programs', ProgramViewSet)
router.register('workouts', WorkoutViewSet)
router.register('exercises', ExerciseViewSet)
router.register('workout-exercises', WorkoutExerciseViewSet)
router.register("appointments", AppointmentViewSet)
router.register("progress", ClientProgressViewSet)
router.register("clients", ClientViewSet)
router.register("exercise-progress", ExerciseProgressViewSet)
router.register("subscriptions", SubscriptionViewSet)
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('', include(router.urls)),
    path('trainer-signup/',TrainerSignupView.as_view()),
    path("ai/training-plan/", AITrainingPlanView.as_view()),
    path("me/", MeView.as_view()),
]