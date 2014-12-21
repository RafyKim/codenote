from django.contrib import admin
from note.models import *

# Register your models here.
admin.site.register(Topic)
admin.site.register(Note)
admin.site.register(CodenoteUser)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Collection)
