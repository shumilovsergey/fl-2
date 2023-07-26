from django.contrib import admin
from .models import Chats
from .models import Moderators
from .models import Janras
from .models import Storys

admin.site.register(Chats)
admin.site.register(Moderators)
admin.site.register(Janras)
admin.site.register(Storys)