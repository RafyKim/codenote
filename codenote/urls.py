from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'codenote.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include('note.urls', namespace="note")),
    # url(r'^ckeditor/', include('ckeditor.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),

)
