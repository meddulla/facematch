from logging import getLogger
from django.contrib import admin

from .models import MissingPerson, UnidentifiedPerson, MissingFace, UnidentifiedFace, FaceMatch


logger = getLogger(__name__)


class FaceMatchInline(admin.TabularInline):
    model = FaceMatch
    fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity', 'human_verified',
              'case_info_checked', 'case_info_reasons_non_match',)
    readonly_fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity', 'bounding_box',
                       'case_info_checked', 'case_info_reasons_non_match')
    extra = 0

class UnidentifiedPersonAdmin(admin.ModelAdmin):
    model = UnidentifiedPerson
    list_display = ('code', 'ethnicity', 'est_min_age', 'est_max_age', 'has_case_info', 'last_fetched')
    readonly_fields = ('photo_tag',)
    search_fields = ('code', )
    list_filter = ('has_case_info',)


class MissingPersonAdmin(admin.ModelAdmin):
    model = MissingPerson
    list_display = ('code', 'name','has_case_info', 'last_fetched')
    readonly_fields = ('photo_tag',)
    search_fields = ('code', 'has_case_info', 'name')
    list_filter = ('has_case_info',)

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
    list_display = ('id', 'missing_person', 'similarity', 'human_verified', 'human_says_maybe',  'case_info_checked',
                    'case_info_matches')
    readonly_fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity', 'bounding_box',
                        'case_info_checked', 'case_info_reasons_non_match', 'case_info_matches', 'case_info_last_checked')

    search_fields = ('missing_person__code', 'missing_person__name')
    list_filter = ('human_verified', 'human_says_maybe', 'case_info_checked', 'case_info_matches')




# Register your models here.
admin.site.register(MissingPerson, MissingPersonAdmin)
admin.site.register(MissingFace, MissingFaceAdmin)
admin.site.register(UnidentifiedPerson, UnidentifiedPersonAdmin)
admin.site.register(UnidentifiedFace, UnidentifiedFaceAdmin)
admin.site.register(FaceMatch, FaceMatchAdmin)


# admin.site.disable_action('delete_selected')
admin.site.site_header = "Face Match"
admin.site.index_title = "Admin"
