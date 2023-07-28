import json

import requests
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponse
from web.forms.file import FileModelForm, FilePutModelForm
from web import models
from django.forms import model_to_dict
from web.utils.tencent.cos import delete_file, delete_files,credential


def file(request, project_id):
    parent_object = None
    folder_id = request.GET.get('folder', '')
    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=folder_id, file_type=2,
                                                             project=request.tracer.project).first()

    if request.method == 'GET':
        parent = parent_object
        navbar_list = []
        while parent:
            navbar_list.insert(0, model_to_dict(parent, ['id', 'name']))
            parent = parent.parent
        form = FileModelForm(request, parent_object)
        query_set = models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            file_object_list = query_set.filter(parent=parent_object).order_by('-file_type')
        else:
            file_object_list = query_set.filter(parent=None).order_by('-file_type')
        return render(request, 'file.html',
                      {"form": form,
                       'file_object_list': file_object_list,
                       'navbar_list': navbar_list,
                       'folder_id': folder_id})

    fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():
        edit_object = models.FileRepository.objects.filter(id=fid, file_type=2, project=request.tracer.project).first()
    if edit_object:
        form = FileModelForm(request, parent_object, data=request.POST, instance=edit_object)
    else:
        form = FileModelForm(request, parent_object, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.parent = parent_object
        form.instance.update_user = request.tracer.user
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def file_delete(request, project_id):
    fid = request.GET.get('fid')
    delete_object = models.FileRepository.objects.filter(id=fid, project=request.tracer.project).first()
    if delete_object.file_type == 1:
        # 删除文件：1.归还所使用的空间
        request.tracer.project.use_space -= delete_object.file_size
        request.tracer.project.save()
        # 删除文件：2.将cos中的文件也删除
        delete_file(request.tracer.project.region, request.tracer.project.bucket, delete_object.key)
        # 删除文件：3.将文件在数据库中删除
        delete_object.delete()
        return JsonResponse({"status": True})

    # 删除文件夹，同时删除该文件夹下的所有文件和文件夹
    # 该文件夹下所有文件的使用容量汇总，用户归还项目空间容量
    total_size = 0
    # 该文件夹下所有文件的key
    key_list = []
    # 该文件夹下所有的文件夹列表
    folder_list = [delete_object, ]
    # 循环文件夹列表，找出数据库中的以该文件夹为父级目录的所有文件夹和文件
    for folder in folder_list:
        # 找出数据库中的以该文件夹为父级目录的所有文件夹和文件
        child_list = models.FileRepository.objects.filter(project=request.tracer.project, parent=folder).order_by(
            '-file_type')
        for child in child_list:
            if child.file_type == 2:
                # 如果是文件夹，加入文件夹列表
                folder_list.append(child)
            else:
                # 如果是文件，将文件大小汇总，并将文件的key加入key列表
                total_size += child.file_size
                key_list.append({"Key": child.key})
    # 归还使用空间
    request.tracer.project.use_space -= total_size
    request.tracer.project.save()
    # 删除cos中的所有文件
    delete_files(request.tracer.project.region, request.tracer.project.bucket, key_list)
    # 删除数据库中的所有文件和文件夹
    delete_object.delete()
    return JsonResponse({"status": True})


def cos_credential(request, project_id):
    """ 获取cos上传临时凭证 """
    per_file_limit = request.tracer.price_policy.per_file_size * 1024 * 1024
    total_file_limit = request.tracer.price_policy.project_space * 1024 * 1024 * 1024

    total_size = 0
    file_list = json.loads(request.body.decode('utf-8'))
    for item in file_list:
        # 文件的字节大小 item['size'] = B
        # 单文件限制的大小 M
        # 超出限制
        if item['size'] > per_file_limit:
            msg = "单文件超出限制（最大{}M），文件：{}，请升级套餐。".format(request.tracer.price_policy.per_file_size, item['name'])
            return JsonResponse({'status': False, 'error': msg})
        total_size += item['size']

        # 做容量限制：单文件 & 总容量

    # 总容量进行限制
    # request.tracer.price_policy.project_space  # 项目的允许的空间
    # request.tracer.project.use_space # 项目已使用的空间
    if request.tracer.project.use_space + total_size > total_file_limit:
        return JsonResponse({'status': False, 'error': "容量超过限制，请升级套餐。"})

    data_dict = credential(request.tracer.project.bucket, request.tracer.project.region)
    return JsonResponse({'status': True, 'data': data_dict})


def file_post(request, project_id):
    """ 已上传成功的文件写入到数据 """
    """
    name: fileName,
    key: key,
    file_size: fileSize,
    parent: CURRENT_FOLDER_ID,
    # etag: data.ETag,
    file_path: data.Location
    """

    # 根据key再去cos获取文件Etag和"db7c0d83e50474f934fd4ddf059406e5"

    # 把获取到的数据写入数据库即可
    form = FilePutModelForm(request, data=request.POST)
    if form.is_valid():
        # 通过ModelForm.save存储到数据库中的数据返回的isntance对象，无法通过get_xx_display获取choice的中文
        form.instance.file_type = 1

        form.instance.project = request.tracer.project
        form.instance.update_user = request.tracer.user
        form.instance.parent_id = request.POST.get("parent")
        instance = form.save() # 添加成功之后，获取到新添加的那个对象（instance.id,instance.name,instance.file_type,instace.get_file_type_display()

        # 校验通过：数据写入到数据库

        # 项目的已使用空间：更新 (data_dict['file_size'])
        request.tracer.project.use_space += instance.file_size
        request.tracer.project.save()

        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            "file_path": instance.file_path,
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime('%Y{y}%m{m}%d{d} %H:%M').format(y='年', m='月', d='日'),
            'download_url': reverse('web:file_download', kwargs={"project_id": project_id, 'file_id': instance.id})
        }
        return JsonResponse({'status': True, 'data': result})

    return JsonResponse({'status': False, 'data': form.errors})


def file_download(request, project_id, file_id):
    """ 下载文件 """

    file_object = models.FileRepository.objects.filter(id=file_id, project_id=project_id).first()
    res = requests.get(file_object.file_path)

    # 文件分块处理（适用于大文件）
    data = res.iter_content()

    # 设置content_type=application/octet-stream 用于提示下载框
    response = HttpResponse(data, content_type="application/octet-stream")
    from django.utils.encoding import escape_uri_path

    # 设置响应头：中文件文件名转义
    response['Content-Disposition'] = "attachment; filename={};".format(escape_uri_path(file_object.name))
    return response