from django.utils.deprecation import MiddlewareMixin
from web import models
from django.shortcuts import redirect, render
from django.conf import settings
import datetime


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.tracer = Tracer()
        user_id = request.session.get("user_id", 0)
        user_obj = models.UserInfo.objects.filter(id=user_id).first()
        request.tracer.user = user_obj
        if request.path_info in settings.VALID_PATH:
            return
        if request.tracer.user:
            transaction = models.Transaction.objects.filter(user=user_obj, status=2).order_by('-id').first()
            if transaction and transaction.end_datetime > datetime.datetime.now():
                price_policy = transaction.price_policy
            else:
                price_policy = models.PricePolicy.objects.filter(category=1, title='个人免费版').first()
            request.tracer.price_policy = price_policy
            return
        return redirect('/login/')

    def process_view(self, request, view, args, kwargs):
        if not request.path_info.startswith('/manage/'):
            return

        project_id = kwargs.get('project_id')
        project_object = models.Project.objects.filter(creator=request.tracer.user, id=project_id).first()
        if project_object:
            request.tracer.project = project_object
            return
        join_project_object = models.ProjectUser.objects.filter(user=request.tracer.user, project_id=project_id).first()
        if join_project_object:
            request.tracer.project = join_project_object.project
            return
        return render(request, '404.html')
