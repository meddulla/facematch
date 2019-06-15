from logging import getLogger
from django.contrib import admin
from django.utils.safestring import mark_safe
from facematch.storage_backends import MissingStorage, UnidentifiedStorage

from .models import MissingPerson, UnidentifiedPerson, MissingFace, UnidentifiedFace, FaceMatch


logger = getLogger(__name__)


def make_not_a_face(modeladmin, request, queryset):
    queryset.update(is_face=False)
make_not_a_face.short_description = "Mark selected faces as not a face"


def make_a_tattoo(modeladmin, request, queryset):
    queryset.update(object_type="tattoo", is_face=False)
make_a_tattoo.short_description = "Mark selected as a tattoo"


class FaceMatchInline(admin.TabularInline):
    model = FaceMatch
    fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity', 'human_verified',
              'case_info_checked', 'case_info_reasons_non_match',)
    readonly_fields = ('missing', 'missing_tag', 'unidentified', 'unidentified_tag', 'similarity', 'bounding_box',
                       'case_info_checked', 'case_info_reasons_non_match')
    extra = 0

class UnidentifiedPersonAdmin(admin.ModelAdmin):
    model = UnidentifiedPerson
    list_display = ('code', 'ethnicity', 'est_min_age', 'est_max_age', 'has_case_info',
                    'last_fetched')
    readonly_fields = ('photo_tag',)
    search_fields = ('code', )
    list_filter = ('has_case_info',)
    change_list_template = "bo/change_list.html"


class MissingPersonAdmin(admin.ModelAdmin):
    model = MissingPerson
    list_display = ('code', 'name','has_case_info', 'last_fetched')
    readonly_fields = ('photo_tag',)
    search_fields = ('code', 'has_case_info', 'name')
    list_filter = ('has_case_info',)
    change_list_template = "bo/change_list.html"

    inlines = [
        FaceMatchInline,
    ]

class MissingFaceAdmin(admin.ModelAdmin):
    model = MissingFace
    list_display = ('id', 'is_face', 'person', 'searched', 'last_searched', 'photo_tag_listing')
    fields = ('person', 'photo', 'is_face', 'photo_tag', 'searched', 'last_searched')
    readonly_fields = ('photo_tag', 'searched', 'last_searched')
    list_filter = ('is_face', 'searched')
    actions = [make_not_a_face]
    change_list_template = "bo/change_list.html"

    def photo_tag_listing(self, obj):
        url = "https://%s/%s" % (MissingStorage.custom_domain, obj.photo)
        return mark_safe('<a href="%s" target="_blank"><img src="%s" width="50px" alt="%s"/></a>' % (url, url, obj.photo))

class UnidentifiedFaceAdmin(admin.ModelAdmin):
    model = UnidentifiedFace
    list_display = ('id', 'is_face', 'person', 'photo_tag_listing')
    # fields = ('person','photo', 'is_face', 'photo_tag',)
    readonly_fields = ('id', 'photo_tag', 'in_collection', 'bounding_box', 'photo')
    list_filter = ('is_face',)
    actions = [make_not_a_face, make_a_tattoo]
    change_list_template = "bo/change_list.html"

    def photo_tag_listing(self, obj):
        url = "https://%s/%s" % (UnidentifiedStorage.custom_domain, obj.photo)
        return mark_safe('<a href="%s" target="_blank"><img src="%s" width="50px" alt="%s"/></a>' % (url, url, obj.photo))


class FaceMatchAdmin(admin.ModelAdmin):
    model = FaceMatch
    list_display = ('id', 'missing_person', 'missing_person_last_sighted', 'unidentified', 'similarity', 'human_verified', 'human_says_maybe',  'case_info_checked',
                    'case_info_matches')
    readonly_fields = ('missing', 'missing_person_last_sighted', 'missing_tag', 'mnameus_link', 'unidentified', 'unidentified_tag', 'unameus_link', 'similarity', 'bounding_box',
                        'case_info_checked', 'case_info_reasons_non_match', 'case_info_matches', 'case_info_last_checked')

    search_fields = ('missing_person__code', 'missing_person__name')
    list_filter = ('human_verified', 'human_says_maybe', 'case_info_checked', 'case_info_matches', 'missing_person__last_sighted')
    change_list_template = "bo/change_list.html"




# Register your models here.
admin.site.register(MissingPerson, MissingPersonAdmin)
admin.site.register(MissingFace, MissingFaceAdmin)
admin.site.register(UnidentifiedPerson, UnidentifiedPersonAdmin)
admin.site.register(UnidentifiedFace, UnidentifiedFaceAdmin)
admin.site.register(FaceMatch, FaceMatchAdmin)


# admin.site.disable_action('delete_selected')
admin.site.site_header = "Face Match"
admin.site.index_title = "Admin"
