from logging import getLogger
from django.contrib import admin

from .models import MissingPerson, UnidentifiedPerson, MissingFace, UnidentifiedFace, FaceMatch


logger = getLogger(__name__)


class FaceMatchInline(admin.TabularInline):
    model = FaceMatch
    fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity')
    readonly_fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity', 'bounding_box')
    extra = 0

class UnidentifiedPersonAdmin(admin.ModelAdmin):
    model = UnidentifiedPerson
    fields = ('code', 'gender', 'photo', 'photo_tag',)
    readonly_fields = ('photo_tag',)


class MissingPersonAdmin(admin.ModelAdmin):
    model = MissingPerson
    fields = ('code', 'name', 'photo', 'photo_tag',)
    readonly_fields = ('photo_tag',)

    inlines = [
        FaceMatchInline,
    ]

class MissingFaceAdmin(admin.ModelAdmin):
    model = MissingFace
    list_display = ('id', 'is_face', 'person', 'searched', 'last_searched')
    fields = ('person', 'photo', 'is_face', 'photo_tag', 'searched', 'last_searched')
    readonly_fields = ('photo_tag', 'searched', 'last_searched')

class UnidentifiedFaceAdmin(admin.ModelAdmin):
    model = UnidentifiedFace
    list_display = ('id', 'is_face', 'person')
    fields = ('person','photo', 'is_face', 'photo_tag',)
    readonly_fields = ('photo_tag',)

class FaceMatchAdmin(admin.ModelAdmin):
    model = FaceMatch
    list_display = ('id', 'missing_person', 'similarity', 'human_verified', 'human_says_maybe')
    fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity', 'bounding_box',
              'human_verified', 'human_says_maybe')
    readonly_fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity', 'bounding_box')





# Register your models here.
admin.site.register(MissingPerson, MissingPersonAdmin)
admin.site.register(MissingFace, MissingFaceAdmin)
admin.site.register(UnidentifiedPerson, UnidentifiedPersonAdmin)
admin.site.register(UnidentifiedFace, UnidentifiedFaceAdmin)
admin.site.register(FaceMatch, FaceMatchAdmin)


# admin.site.disable_action('delete_selected')

admin.site.index_title = "Admin"
