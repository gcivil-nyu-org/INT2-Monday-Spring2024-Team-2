from django.contrib import admin

# Register your models here.

from .models import (
    UserType,
    Expertise,
    Availability,
    ProfileS,
    ProfileT,
    TutoringSession,
)

admin.site.register(UserType)
admin.site.register(Expertise)
admin.site.register(Availability)
admin.site.register(ProfileS)
admin.site.register(ProfileT)
admin.site.register(TutoringSession)
