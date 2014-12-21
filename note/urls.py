#-*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from note.views import *
# from allauth import account
# from allauth.account.views import login


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^note/add/$', NoteAddView.as_view(), name='addnote'),
    url(r'^note/edit/(?P<pk>\d+)/$', NoteEditView.as_view(), name='editnote'),
    url(r'^note/read/(?P<pk>\d+)/$', NoteReadView.as_view(), name='readnote'),

    url(r'^search/$', SearchView.as_view(), name='search'),
    url(r'^recommend/$', RecommendView.as_view(), name='recommend'),

    url(r'^user/$', UserRedirectView.as_view(), name='userredirect'),
    url(r'^topic/(?P<name>[-\w]+)/$', TopicView.as_view(), name='topicview'),

    url(r'^(?P<username>[-\w]+)/$', UserNotesView.as_view(), name='usernotes'),
    url(r'^(?P<username>[-\w]+)/collection/$', UserCollectionsView.as_view(), name='usercollections'),

    url(r'^ajax/note/add/$', add_note, name='add_note'),
    url(r'^ajax/note/del/$', del_note, name='delnote'),
    url(r'^ajax/note/edit/$', edit_note, name='edit_note'),
    url(r'^ajax/cmt/add/$', add_cmt, name='add_cmt'),
    url(r'^ajax/cmt/del/$', del_cmt, name='del_cmt'),
    url(r'^ajax/note/collect/$', collect_note, name='collectnote'),
    url(r'^ajax/note/decollect/$', decollect_note, name='decollectnote'),

    # url(r'^comment/insert/$', comment_insert, name='comment_insert'),


)