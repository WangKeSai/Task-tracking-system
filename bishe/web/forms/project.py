from django import forms
from web import models
from web.forms.account import BootStrapForm
from django.core.exceptions import ValidationError
from web.forms.widgets import ColorRadioSelect


class AddProjectModelForm(BootStrapForm, forms.ModelForm):
    bootstrap_class_exclude = ['color']
    class Meta:
        model = models.Project
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea,
            'color': ColorRadioSelect(attrs={'class': 'color-radio'})
        }

    def __init__(self,request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data['name']
        exists = models.Project.objects.filter(name=name, creator=self.request.tracer.user).exists()
        if exists:
            raise ValidationError("该项目名已存在！")
        all_count = models.Project.objects.filter(creator=self.request.tracer.user).count()
        if all_count >= self.request.tracer.price_policy.project_num:
            raise ValidationError("新建项目数已用完！")
        return name

