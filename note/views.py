#-*- coding: utf-8 -*-

from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.utils.html import strip_tags
from django.http import HttpResponse
from django.db.models import Q
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView, FormView
from note.models import Note, CodenoteUser, Topic, Comment, Like, Collection
from django.template import loader, Context

from endless_pagination.views import AjaxListView

from django.core.urlresolvers import reverse
import json
import re
from BeautifulSoup import BeautifulSoup
# from note import forms

# Create your views here.
from django.conf import settings
from allauth.socialaccount.models import SocialAccount
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.views import RedirectAuthenticatedUserMixin

# 한글 인코딩 ASCII --> UTF-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def user_img(uid):
    # User Image
    user = CodenoteUser.objects.get(pk=uid)
    if user.img:
        img = user.img
    else:

        user = SocialAccount.objects.filter(user_id=uid)
        if user:
            if user[0].provider == 'google':
                img = user[0].extra_data['picture']
            elif user[0].provider == 'facebook':
                img = "http://graph.facebook.com/"+str(user[0].uid)+"/picture"
            else:
                pass
        else:
            img = '/static/img/noimage.png'

    return img


def stripcode(data):
    p = re.compile(r'<pre>(.*?)</pre>')
    return p.sub('', data)


class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        path = "/accounts/{username}/"
        return path.format(username=request.user.username)


class IndexView(RedirectAuthenticatedUserMixin, TemplateView):
    template_name = 'index.html'
    redirect_field_name = 'usernotes'

    def get_success_url(self):
        return "/"+str(self.request.user.username)+"/"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        return context

class UserRedirectView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        user_id = self.request.user.id
        user = CodenoteUser.objects.filter(id=user_id)
        if len(user) == 0:
            return False
        return redirect('/'+user[0].username)


class UserNotesView(AjaxListView):
    model = Note
    template_name = 'usernotes.html'
    page_template = 'notes.html'
    context_object_name = 'notes'

    def get_queryset(self):
        user = CodenoteUser.objects.filter(username__exact=self.kwargs['username'])
        notes = Note.objects.filter(user_id=user[0].id).order_by('-id')

        # Code 삭제하고 문자열 줄이기
        for n in notes:
            soup = BeautifulSoup(n.content)
            pres = soup.findAll("pre")

            for p in pres:
                n.content = n.content.replace(str(p), '')
            n.name = n.name[:50] + "..."
            n.content = n.content[:150] + "..."
            n.cnt_col = Collection.objects.filter(note_id=n.id).count()
            n.cnt_cmt = Comment.objects.filter(note_id=n.id).count()
            n.user_img = user_img(n.user.id)

        return notes

    def get_context_data(self, **kwargs):
        context = super(UserNotesView, self).get_context_data(**kwargs)

        return context


class UserCollectionsView(AjaxListView):
    model = Note
    template_name = 'usercollections.html'
    page_template = 'notes.html'
    context_object_name = 'notes'

    def get_queryset(self):
        user = CodenoteUser.objects.filter(username__exact=self.kwargs['username'])
        collections = Collection.objects.filter(user_id=user[0].id).order_by('-id')

        notes = []
        for c in collections:
            notes.append(c.note)

        # Code 삭제하고 문자열 줄이기
        for n in notes:
            soup = BeautifulSoup(n.content)
            pres = soup.findAll("pre")

            for p in pres:
                n.content = n.content.replace(str(p), '')
            n.name = n.name[:50] + "..."
            n.content = n.content[:150] + "..."
            n.cnt_col = Collection.objects.filter(note_id=n.id).count()
            n.cnt_cmt = Comment.objects.filter(note_id=n.id).count()
            n.user_img = user_img(n.user.id)

        return notes

    def get_context_data(self, **kwargs):
        context = super(UserCollectionsView, self).get_context_data(**kwargs)

        return context



class RecommendView(AjaxListView):
    model = Note
    template_name = 'recommend.html'
    page_template = 'notes.html'
    context_object_name = 'notes'

    def get_queryset(self):
        # 내가 작성한 노트들에서 Topic들을 추출
        my_notes = Note.objects.filter(user_id = self.request.user.id)
        my_topics = []
        for my_note in my_notes:
            tmp_topics = my_note.topic.all()
            for t in tmp_topics:
                if t not in my_topics:
                    my_topics.append(t)

        # 내가 다루었던 Topic들을 다루는 노트들을 추출
        tmp_notes = Note.objects.exclude(user_id = self.request.user.id).exclude(isPublic = 0).order_by('-id')
        notes = []
        for tmp_note in tmp_notes:
            tmp_topics = tmp_note.topic.all()
            for t in tmp_topics:
                if t in my_topics:
                    if tmp_note not in notes:
                        notes.append(tmp_note)

        # Code 삭제하고 문자열 줄이기
        for n in notes:
            soup = BeautifulSoup(n.content)
            pres = soup.findAll("pre")

            for pre in pres:
                n.content = n.content.replace(str(pre), '')

            n.name = n.name[:50] + "..."
            n.content = n.content[:150] + "..."
            n.cnt_col = Collection.objects.filter(note_id=n.id).count()
            n.cnt_cmt = Comment.objects.filter(note_id=n.id).count()
            n.user_img = user_img(n.user.id)

        return notes

    def get_context_data(self, **kwargs):
        context = super(RecommendView, self).get_context_data(**kwargs)

        return context


class SearchView(AjaxListView):
    model = Note
    template_name = 'search.html'
    page_template = 'notes.html'
    context_object_name = 'notes'

    def get_queryset(self):
        query = self.request.GET.get('query')
        notes = []

        if query:
            # DB검색은 제외하고, 인덱스 검색으로 교체한다.
            notes1 = Note.objects.filter(name__contains=query).order_by('-id')
            for n in notes1:
                notes.append(n)
            notes2 = Note.objects.filter(content__contains=query).order_by('-id')
            for n in notes2:
                if n not in notes:
                    notes.append(n)

            topics1 = Topic.objects.filter(name__contains=query).order_by('-id')
            for t in topics1:
                notes3 = t.note_set.all()
                for n in notes3:
                    if n not in notes:
                        notes.append(n)
            topics2 = Topic.objects.filter(content__contains=query).order_by('-id')
            for t in topics2:
                notes4 = t.note_set.all()
                for n in notes4:
                    if n not in notes:
                        notes.append(n)

        # Code 삭제하고 문자열 줄이기
        for n in notes:
            soup = BeautifulSoup(n.content)
            pres = soup.findAll("pre")

            for p in pres:
                n.content = n.content.replace(str(p), '')
            n.name = n.name[:50] + "..."
            n.content = n.content[:150] + "..."
            n.cnt_col = Collection.objects.filter(note_id=n.id).count()
            n.cnt_cmt = Comment.objects.filter(note_id=n.id).count()
            n.user_img = user_img(n.user.id)

            if n.isPublic == 0:
                notes.remove(n)

        return notes

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        return context


class TopicView(AjaxListView):
    model = Note
    template_name = 'topic.html'
    page_template = 'notes.html'
    context_object_name = 'notes'

    def get_queryset(self):
        topic = Topic.objects.filter(name__exact=self.kwargs['name'])
        notes = topic[0].note_set.all()

        # Code 삭제하고 문자열 줄이기
        for n in notes:
            soup = BeautifulSoup(n.content)
            pres = soup.findAll("pre")

            for p in pres:
                n.content = n.content.replace(str(p), '')
            n.name = n.name[:50] + "..."
            n.content = n.content[:150] + "..."
            n.cnt_col = Collection.objects.filter(note_id=n.id).count()
            n.cnt_cmt = Comment.objects.filter(note_id=n.id).count()
            n.user_img = user_img(n.user.id)

        return notes

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['topic'] = Topic.objects.filter(name__exact=self.kwargs['name'])[0]

        return context


class NoteReadView(TemplateView):
    template_name = 'note/read.html'

    def get_context_data(self, **kwargs):
        context = super(NoteReadView, self).get_context_data(**kwargs)

        chk_col = Collection.objects.filter(note_id=self.kwargs['pk'], user_id=self.request.user.id)
        if chk_col:
            context['chk_col'] = 1
        else:
            context['chk_col'] = 0

        cmts = Comment.objects.filter(note_id=self.kwargs['pk']).order_by('-id')
        for c in cmts:
            c.user_img = user_img(c.user.id)
        context['cmts'] = cmts

        note = Note.objects.get(id=self.kwargs['pk'])

        context['canRead'] = True
        if note.isPublic == 0:
            if note.user != self.request.user:
                context['canRead'] = False

        if context['canRead']:
            note.cnt_col = Collection.objects.filter(note_id=self.kwargs['pk']).count()
            note.cnt_cmt = cmts.count()
            note.user_img = user_img(note.user.id)

            context['n'] = note

        if self.request.user.id:
            context['my_img'] = user_img(self.request.user.id)

        return context


class NoteAddView(TemplateView):
    template_name = 'note/add.html'

    def get_context_data(self, **kwargs):
        context = super(NoteAddView, self).get_context_data(**kwargs)
        # cnt_ratings = Rating.objects.filter(user_id=self.request.user.id).count()
        context['topics'] = Topic.objects.all()

        return context



class NoteEditView(TemplateView):
    template_name = 'note/edit.html'

    # 사용자 ID와 세션 ID 대조하여 redirect 처리 필요

    def get_context_data(self, **kwargs):
        context = super(NoteEditView, self).get_context_data(**kwargs)
        context['n'] = Note.objects.get(id=self.kwargs['pk'])

        return context


def add_note(request, **kwargs):
    user_id = request.user.id

    if request.is_ajax():
        new_note = Note()
        new_note.user_id = user_id
        new_note.name = request.POST.get('name', '')
        if new_note.name == '':
            new_note.name = '제목 없음'

        new_note.content = request.POST.get('content', '')
        if new_note.content == '':
            new_note.content = '내용 없음'

        if request.POST.get('isNotPublic') == 'true':
            new_note.isPublic = False

        new_note.save()

        tmp_topic = request.POST.get('topic', '')
        tmp_topic = tmp_topic.split(':$&*:')
        tmp_topic.pop()

        for t in tmp_topic:
            chk_t = Topic.objects.filter(name__exact=t)
            # 동일한 Topic이 아직 없다면
            if chk_t.count() == 0:
                topic = Topic()
                topic.name = t
                topic.save()
                new_note.topic.add(topic.id)

            # 동일한 Topic이 이미 있다면
            else:
                new_note.topic.add(chk_t[0].id)

        return to_json({'status': 'success', 'id': new_note.id })

    else:
        return to_json({'status': 'failed'})




def del_note(request, **kwargs):
    user_id = request.user.id

    if request.is_ajax():
        note = Note.objects.get(pk=int(request.POST.get('note_id')))
        if note.user_id == user_id:
            note.delete()
            return to_json({'status': 'success'})
        else:
            return to_json({'status': 'failed'})

    else:
        return to_json({'status': 'failed'})


def edit_note(request, **kwargs):
    user_id = request.user.id

    if request.is_ajax():
        note = Note.objects.get(pk=int(request.POST.get('note_id')))
        if note.user_id == user_id:

            note.user_id = user_id
            note.name = request.POST.get('name', '')
            if note.name == '':
                note.name = '제목 없음'

            note.content = request.POST.get('content', '')
            if note.content == '':
                note.content = '내용 없음'

            if request.POST.get('isNotPublic') == 'true':
                note.isPublic = False

            note.save()

            tmp_topic = request.POST.get('topic', '')
            tmp_topic = tmp_topic.split(':$&*:')
            tmp_topic.pop()

            note.topic.clear()

            for t in tmp_topic:
                chk_t = Topic.objects.filter(name__exact=t)
                # 동일한 Topic이 아직 없다면
                if chk_t.count() == 0:
                    topic = Topic()
                    topic.name = t
                    topic.save()
                    note.topic.add(topic.id)

                # 동일한 Topic이 이미 있다면
                else:
                    note.topic.add(chk_t[0].id)

            return to_json({'status': 'success'})
        else:
            return to_json({'status': 'failed'})

    else:
        return to_json({'status': 'failed'})


def collect_note(request, **kwargs):
    user_id = request.user.id

    if request.is_ajax():
        new_collect = Collection()
        new_collect.user_id = user_id
        new_collect.note_id = request.POST.get('note_id', '')
        new_collect.content = request.POST.get('content', '')
        new_collect.save()

        return to_json({'status': 'success', 'id': new_collect.id })

    else:
        return to_json({'status': 'failed'})


def decollect_note(request, **kwargs):
    if request.is_ajax():
        chk_collect = Collection.objects.filter(note_id=int(request.POST.get('note_id')), user_id=request.user.id)
        if chk_collect:
            for c in chk_collect:
                c.delete();
            return to_json({'status': 'success'})

        else:
            return to_json({'status': 'failed'})

    else:
        return to_json({'status': 'failed'})



def add_cmt(request):
    user_id = request.user.id

    if request.is_ajax():
        new_cmt = Comment()
        new_cmt.user_id = user_id
        new_cmt.note_id = request.POST.get('note_id', '')
        new_cmt.content = request.POST.get('content', '')
        new_cmt.save()

        new_cmt.user_img = user_img(user_id)

        csrf_token = request.POST.get('csrfmiddlewaretoken')

        t = loader.get_template('comment.html')
        c = Context({ 'c': new_cmt, 'csrf_token': csrf_token })

        return HttpResponse(t.render(c))

    else:
        return to_json({'status': 'failed'})


def del_cmt(request, **kwargs):
    user_id = request.user.id

    if request.is_ajax():
        cmt = Comment.objects.get(pk=int(request.POST.get('cmt_id')))
        if cmt.user_id == user_id:
            cmt.delete()
            return to_json({'status': 'success'})
        else:
            return to_json({'status': 'failed'})


    else:
        return to_json({'status': 'failed'})




def to_json(objs, status=200):
    j = json.dumps(objs, ensure_ascii=False)
    return HttpResponse(j, status=status,
                        content_type='application/json; charset=utf-8')
