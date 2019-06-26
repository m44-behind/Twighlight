from django.contrib import admin
from .models import Streamer, Video, Data


@admin.register(Streamer)
class StreamerAdmin(admin.ModelAdmin):
    list_display = ('login', 'name', 'profile_image_url', )
    #readonly_fields = ['profile_image_url']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'duration' )
    #readonly_fields = ['streamer_id', 'url', 'thumb_nail_url' ]

admin.site.register(Data)