from web.forms.account import BootStrapForm
from django import forms
from web import models
from django.core.exceptions import ValidationError


class EditProjectModelForm(BootStrapForm, forms.ModelForm):
    bootstrap_class_exclude = ['color']

    class Meta:
        model = models.Project
        fields = ['name', 'desc']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data['name']
        exists = models.Project.objects.exclude(id=self.request.tracer.project.id).filter(name=name, creator=self.request.tracer.user).exists()
        if exists:
            raise ValidationError("该项目名已存在！")
        all_count = models.Project.objects.filter(creator=self.request.tracer.user).count()
        return name


class IssuesTypeModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.IssuesType
        fields = ['title']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_title(self):
        title = self.cleaned_data['title']
        exists = models.IssuesType.objects.filter(project=self.request.tracer.project, title=title).exists()
        if exists:
            raise ValidationError("该问题类型已存在")
        return title


class IssuesModuleModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Module
        fields = ['title']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_title(self):
        title = self.cleaned_data['title']
        exists = models.Module.objects.filter(project=self.request.tracer.project, title=title).exists()
        if exists:
            raise ValidationError("该问题模块已存在")
        return title
