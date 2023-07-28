from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from web.forms.project import AddProjectModelForm
from web import models
import time
from web.utils.tencent.cos import creat_bucket


def project_list(request):
    if request.method == 'GET':
        form = AddProjectModelForm(request)
        star_project_list = []
        creat_project_list = []
        join_project_list = []

        # 我创建的项目
        creat_project = models.Project.objects.filter(creator=request.tracer.user).all()
        # 我参与的项目
        join_project = models.ProjectUser.objects.filter(user=request.tracer.user).all()

        for item in creat_project:
            if item.star:
                star_project_list.append({"value": item, "type": "my"})
                continue
            creat_project_list.append(item)

        for item in join_project:
            if item.star:
                star_project_list.append({"value": item.project, "type": "join"})
                continue
            join_project_list.append(item.project)

        return render(request, 'project_list.html', {"form": form,
                                                     "star_project_list": star_project_list,
                                                     "creat_project_list": creat_project_list,
                                                     "join_project_list": join_project_list})

    form = AddProjectModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        name = form.cleaned_data['name']
        bucket = '{}-{}-{}-1314887098'.format(name, request.tracer.user.mobile_phone, str(int(time.time())))
        region = 'ap-beijing'
        form.instance.bucket = bucket
        form.instance.region = region
        creat_bucket(region, bucket)
        instance = form.save()
        # for item in models.IssuesType.PROJECT_INIT_LIST:
        #     models.IssuesType.objects.create(title=item, project=instance)
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def project_star(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=True)
        return redirect('web:project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project__id=project_id, user=request.tracer.user).update(star=True)
        return redirect('web:project_list')
    return render(request, '404.html')


def project_unstar(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=False)
        return redirect('web:project_list')
    if project_type == 'join':
        models.ProjectUser.objects.filter(project__id=project_id, user=request.tracer.user).update(star=False)
        return redirect('web:project_list')
    return render(request, '404.html')
