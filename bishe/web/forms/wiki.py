from django import forms

from web import models
from web.forms.account import BootStrapForm
from django.core.exceptions import ValidationError
from web.forms.widgets import ColorRadioSelect


class AddWikiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        fields = ['title', 'content', 'parent']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        choices = [('', '------------'), ]
        project_list = models.Wiki.objects.filter(project=self.request.tracer.project).values_list('id', 'title')
        choices.extend(project_list)
        self.fields['parent'].choices = choices


class EditWikiModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        fields = ['title', 'content', 'parent']

    def __init__(self, request, wiki_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        choices = [('', '------------'), ]
        project_list = models.Wiki.objects.filter(project=self.request.tracer.project).exclude(id=wiki_id).values_list('id', 'title')
        choices.extend(project_list)
        self.fields['parent'].choices = choices



