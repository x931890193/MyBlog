# Register your models here.
from django.contrib import admin
from .models import AddressInfo, PoemsAuthors, PoetryAuthors, ChinesePoems, \
    RelationPoems, UniversityDepartment, ChineseUniversity

class AddressInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'ddd', 'post_code')
    search_fields = ('id', 'name', 'parent', 'ddd', 'post_code')
    list_per_page = 15


class PoemsAuthorsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'intro_l', 'intro_s', 'dynasty')
    list_per_page = 15


class PoetryAuthorsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'intro', 'dynasty')
    list_per_page = 15


class ChinesePoemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'author_id', 'dynasty', 'author')
    list_per_page = 15


class ChinesePoetryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'yunlv_rule', 'author_id', 'content','dynasty', 'author')
    list_per_page = 15


class UniversityDepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'did', 'name')
    list_per_page = 15


class ChineseUniversityAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'cid', 'name')
    list_per_page = 15

admin.site.register(AddressInfo, AddressInfoAdmin)
admin.site.register(PoemsAuthors, PoemsAuthorsAdmin)
admin.site.register(PoetryAuthors, PoetryAuthorsAdmin)
admin.site.register(ChinesePoems, ChinesePoemsAdmin)
admin.site.register(RelationPoems)
admin.site.register(UniversityDepartment, UniversityDepartmentAdmin)
admin.site.register(ChineseUniversity, ChineseUniversityAdmin)
