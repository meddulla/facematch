from logging import getLogger
from django.contrib import admin

from .models import MissingPerson, UnidentifiedPerson, MissingFace, UnidentifiedFace, FaceMatch


logger = getLogger(__name__)


class UnidentifiedPersonAdmin(admin.ModelAdmin):
    model = UnidentifiedPerson
    fields = ('code', 'gender', 'photo', 'photo_tag',)
    readonly_fields = ('photo_tag',)


class MissingPersonAdmin(admin.ModelAdmin):
    model = UnidentifiedPerson
    fields = ('name', 'gender', 'photo', 'photo_tag',)
    readonly_fields = ('photo_tag',)


# Register your models here.
admin.site.register(MissingPerson, MissingPersonAdmin)
admin.site.register(MissingFace)
admin.site.register(UnidentifiedPerson, UnidentifiedPersonAdmin)
admin.site.register(UnidentifiedFace)
admin.site.register(FaceMatch)


admin.site.disable_action('delete_selected')

admin.site.index_title = "Admin"
