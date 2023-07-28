from django.template import Library
from web import models
from django.shortcuts import reverse

register = Library()


@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    creat_project_list = models.Project.objects.filter(creator=request.tracer.user).all()
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user).all()
    return {"creat_project_list": creat_project_list, "join_project_list": join_project_list, 'request':request}


@register.inclusion_tag('inclusion/manage_menu.html')
def manage_menu(request):
    menu_list = [
        {"title": "概览", "url": reverse("web:dashboard", kwargs={'project_id': request.tracer.project.id})},
        {"title": "问题", "url": reverse("web:issues", kwargs={'project_id': request.tracer.project.id})},
        {"title": "统计", "url": reverse("web:statistics", kwargs={'project_id': request.tracer.project.id})},
        {"title": "文件", "url": reverse("web:file", kwargs={'project_id': request.tracer.project.id})},
        {"title": "wiki", "url": reverse("web:wiki", kwargs={'project_id': request.tracer.project.id})},
        {"title": "配置", "url": reverse("web:setting", kwargs={'project_id': request.tracer.project.id})},
    ]
    for item in menu_list:
        if request.path_info.startswith(item.get('url')):
            item['class'] = 'active'
    return {"menu_list": menu_list}
