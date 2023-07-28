from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from web.utils.tencent.cos import delete_bucket
from web import models
from web.forms.setting import EditProjectModelForm, IssuesTypeModelForm, IssuesModuleModelForm


def setting(request, project_id):
    return render(request, 'setting.html')


def delete(request, project_id):
    if request.tracer.user != request.tracer.project.creator:
        return render(request, '404.html')
    if request.method == 'GET':
        return render(request, 'setting.html', {"navbar": "delete"})
    project_name = request.POST.get("project_name")
    if not project_name or project_name != request.tracer.project.name:
        return render(request, 'setting.html', {"navbar": "delete", "error": "文件名错误！"})
    if request.tracer.project.creator != request.tracer.user:
        return render(request, 'setting.html', {"navbar": "delete", "error": "您没有权限删除该项目！"})
    # 删除cos桶
    delete_bucket(request.tracer.project.bucket, request.tracer.project.region)
    # 删除数据库中项目
    models.Project.objects.filter(id=project_id, creator=request.tracer.user).delete()
    return redirect(reverse("web:project_list"))


def project_info(request, project_id):
    if request.method == 'GET':
        form = EditProjectModelForm(request, instance=request.tracer.project)
        issues_count = models.Issues.objects.filter(project_id=project_id).count()
        file_count = models.FileRepository.objects.filter(project_id=project_id, file_type=1).count()
        wiki_count = models.Wiki.objects.filter(project_id=project_id).count()
        context = {"issues_count": issues_count, "file_count": file_count, "wiki_count": wiki_count,
                   "navbar": "project_info", "form": form}
        return render(request, 'setting.html', context)
    if request.tracer.user != request.tracer.project.creator:
        return render(request, '404.html')
    form = EditProjectModelForm(request, data=request.POST, instance=request.tracer.project)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def project_users(request, project_id):
    if request.method == 'GET':
        all_users = models.ProjectUser.objects.filter(project_id=project_id)
        return render(request, 'setting.html', {"navbar": "project_users", "all_users": all_users})
    if request.tracer.user != request.tracer.project.creator:
        return render(request, '404.html')
    user_id = request.POST.get("p_id")
    if not user_id:
        return JsonResponse({"status": False, "error": "错误！"})
    if request.tracer.project.creator != request.tracer.user:
        return JsonResponse({"status": False, "error": "无权访问！"})
    del_user = models.ProjectUser.objects.filter(id=user_id).first()
    if del_user.project_id != int(project_id):
        return JsonResponse({"status": False, "error": "无权删除！"})
    del_user.delete()
    request.tracer.project.join_count -= 1
    request.tracer.project.save()
    return JsonResponse({"status": True})


def project_issue_type(request, project_id):
    if request.method == 'GET':
        form = IssuesTypeModelForm(request)
        custom_type = models.IssuesType.objects.filter(project_id=project_id)
        return render(request, 'setting.html',
                      {"navbar": "project_issue_type", "custom_type": custom_type, "form": form})
    type_object = None
    if request.POST.get('tid'):
        type_object = models.IssuesType.objects.filter(project_id=project_id, id=request.POST.get('tid')).first()
    form = IssuesTypeModelForm(request, data=request.POST, instance=type_object)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def del_issue_type(request, project_id):
    type_id = request.POST.get('p_id', None)
    type_object = models.IssuesType.objects.filter(project_id=project_id, id=type_id).first()
    if type_object:
        issues_object = models.Issues.objects.filter(project_id=project_id, issues_type_id=type_id).first()
        if issues_object:
            return JsonResponse({"status": False, "error": "当前项目中有问题正在使用该类型，无法删除。"})
        type_object.delete()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": "错误"})


def project_issue_module(request, project_id):
    if request.method == 'GET':
        form = IssuesModuleModelForm(request)
        module_list = models.Module.objects.filter(project_id=project_id)
        return render(request, 'setting.html',
                      {"navbar": "project_issue_module", "form": form, "module_list": module_list})
    module_object = None
    if request.POST.get('tid'):
        module_object = models.Module.objects.filter(project_id=project_id, id=request.POST.get('tid')).first()
    form = IssuesModuleModelForm(request, data=request.POST, instance=module_object)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def del_issue_module(request, project_id):
    module_id = request.POST.get("p_id", None)
    module_project = models.Module.objects.filter(project_id=project_id, id=module_id).first()
    print(module_id)
    if module_project:
        issues_object = models.Issues.objects.filter(project_id=project_id, issues_type_id=module_id).first()
        if issues_object:
            return JsonResponse({"status": False, "error": "当前项目中有问题正在使用该模块，无法删除。"})
        module_project.delete()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": "错误"})

