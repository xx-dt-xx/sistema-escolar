from django.contrib import admin
from .models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag', 'order', 'is_active', 'url')
    list_editable = ('order', 'is_active')
    list_filter = ('tag', 'is_active')
    search_fields = ('name', 'tag')
