from django.contrib import admin

# Register your models here.
from .models import Post, Comment

# customize admin site
class PostAdmin(admin.ModelAdmin):
    # specify fields to be displayed in admin
    list_display = ['title', 'author', 'slug', 'publish', 'status']
    # specify fields to filter by
    list_filter = ['status', 'created', 'publish', 'author']
    # specify field to search in
    search_fields = ['title', 'body']
    # populates slug as title is being typed
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']


class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)