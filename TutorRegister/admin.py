from django.contrib import admin

# Register your models here.

from .models import (
    UserType,
    Expertise,
    Availability,
    ProfileS,
    ProfileT,
    TutoringSession,
    TutorReview,
    Favorite,
    Survey,
)

admin.site.register(UserType)
admin.site.register(Expertise)
admin.site.register(Availability)
admin.site.register(ProfileS)
admin.site.register(ProfileT)
admin.site.register(TutoringSession)
admin.site.register(TutorReview)
admin.site.register(Favorite)
admin.site.register(Survey)
