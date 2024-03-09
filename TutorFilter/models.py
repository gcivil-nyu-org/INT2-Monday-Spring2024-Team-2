from django.db import models
from django.contrib.auth.models import User

import sys

sys.path.insert(0, "../TutorRegister")

# importing the hello
from TutorRegister.models import ProfileT, Availability, Expertise, UserType

# adding Folder_2/subfolder to the system path
