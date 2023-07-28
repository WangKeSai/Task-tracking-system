from django.shortcuts import render, redirect, reverse
from web.forms.wiki import AddWikiModelForm, EditWikiModelForm
from web import models
from django.http import JsonResponse
from web.utils.tencent.cos import upload_file
from web.utils.encrypt import uid


def wiki(request, project_id):
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')
    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, 'wiki.html', {"wiki_object": wiki_object})


def wiki_add(request, project_id):
    if request.method == 'GET':
        form = AddWikiModelForm(request)
        return render(request, 'wiki.html', {"form": form, "type": "add"})
    form = AddWikiModelForm(request, data=request.POST)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project = request.tracer.project
        form.save()
        return redirect(reverse("web:wiki", kwargs={"project_id": project_id}))
    return render(request, 'wiki.html', {"form": form, "type": "add"})


def wiki_catalog(request, project_id):
    data = models.Wiki.objects.filter(project=request.tracer.project).values('id', 'title', 'parent_id').order_by(
        'depth', 'id')
    return JsonResponse({"status": True, "data": list(data)})


def wiki_edit(request, project_id, wiki_id):
    object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    if not object:
        return render(request, '404.html')
    if request.method == 'GET':
        form = EditWikiModelForm(request, wiki_id, instance=object)
        return render(request, 'wiki.html', {"form": form, "type": "edit"})

    form = EditWikiModelForm(request, wiki_id, data=request.POST, instance=object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()
        return redirect(reverse("web:wiki", kwargs={"project_id": project_id}) + "?wiki_id=" + wiki_id)
    return render(request, 'wiki.html', {"form": form, "type": "edit"})


def wiki_del(request, project_id, wiki_id):
    object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    if not object:
        return render(request, '404.html')
    if request.method == 'GET':
        cancel = reverse("web:wiki", kwargs={"project_id": project_id}) + "?wiki_id=" + wiki_id
        return render(request, 'wiki.html', {"type": "del", "cancel": cancel})
    if object.parent:
        models.Wiki.objects.filter(parent=object).update(parent=object.parent)
    else:
        models.Wiki.objects.filter(parent=object).update(parent='')
    object.delete()
    return render(request, 'wiki.html')


def wiki_upload(request, project_id):
    result = {
        'success': 0,
        'message': None,
        'url': None
    }

    image_object = request.FILES.get('editormd-image-file')
    if not image_object:
        result['message'] = "文件不存在"
        return JsonResponse(result)

    ext = image_object.name.rsplit('.')[-1]
    key = "{}.{}".format(uid(request.tracer.user.mobile_phone), ext)
    image_url = upload_file(
        bucket=request.tracer.project.bucket,
        region=request.tracer.project.region,
        file=image_object,
        key=key
    )
    result['success'] = 1
    result['url'] = image_url
    print(result['url'])
    return JsonResponse(result)


