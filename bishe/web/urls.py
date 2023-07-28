from django.conf.urls import url
from django.urls import include

from web.views import account, home, project, statistics, wiki, file, setting, issues, dashboard
from web.views.home import page_not_found

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    url(r'^login/$', account.login, name='login'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    url(r'^image/code/$', account.image_code, name='image_code'),
    url(r'^editpwd/$', account.editpwd, name='editpwd'),

    url(r'^index/$', home.index, name='index'),
    url(r'^$', home.index, name='index'),

    url(r'^price/$', home.price, name='price'),
    url(r'^payment/(?P<policy_id>\d+)/$', home.payment, name='payment'),
    url(r'^payment/history/(?P<order_id>\w+)/$', home.history_payment, name='history_payment'),
    url(r'^pay/$', home.pay, name='pay'),
    url(r'^pay/notify/$', home.pay_notify, name='pay_notify'),
    url(r'^pay/history/$', home.pay_history, name='history'),



    url(r'^project/list/$', project.project_list, name='project_list'),
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),

    url(r'^invite/join/(?P<code>\w+)/$', issues.invite_join, name='invite_join'),

    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^wiki/$', wiki.wiki, name='wiki'),
        url(r'^wiki/add/$', wiki.wiki_add, name='wiki_add'),
        url(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
        url(r'^wiki/del/(?P<wiki_id>\d+)/$', wiki.wiki_del, name='wiki_del'),
        url(r'^wiki/catalog/', wiki.wiki_catalog, name='wiki_catalog'),
        url(r'^wiki/upload/', wiki.wiki_upload, name='wiki_upload'),

        url(r'^file/$', file.file, name='file'),
        url(r'^file/delete/$', file.file_delete, name='file_delete'),
        url(r'^cos/credential/$', file.cos_credential, name='cos_credential'),
        url(r'^file/post/$', file.file_post, name='file_post'),
        url(r'^file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),

        url(r'^setting/$', setting.setting, name='setting'),
        url(r'^setting/delete/$', setting.delete, name='setting_delete'),
        url(r'^setting/project/info/$', setting.project_info, name='setting_project_info'),
        url(r'^setting/project/users/$', setting.project_users, name='setting_project_users'),
        url(r'^setting/project/issue/type/$', setting.project_issue_type, name='setting_project_issue_type'),
        url(r'^setting/del/issue/type/$', setting.del_issue_type, name='setting_del_issue_type'),
        url(r'^setting/project/issue/module/$', setting.project_issue_module, name='setting_project_issue_module'),
        url(r'^setting/del/issue/module/$', setting.del_issue_module, name='setting_del_issue_module'),

        url(r'^issues/$', issues.issues, name='issues'),
        url(r'^issues/detail/(?P<issues_id>\d+)/$', issues.issues_detail, name='issues_detail'),
        url(r'^issues/record/(?P<issues_id>\d+)/$', issues.issues_record, name='issues_record'),
        url(r'^issues/change/(?P<issues_id>\d+)/$', issues.issues_change, name='issues_change'),
        url(r'^issues/invite/url/$', issues.invite_url, name='invite_url'),

        url(r'^dashboard/$', dashboard.dashboard, name='dashboard'),
        url(r'^dashboard/issues/charts/$', dashboard.issues_chart, name='issues_chart'),

        url(r'^statistics/$', statistics.statistics, name='statistics'),
        url(r'^statistics/priority/$', statistics.statistics_priority, name='statistics_priority'),
        url(r'^statistics/project/user/$', statistics.statistics_project_user, name='statistics_project_user'),

    ])),

]

handler404 = 'web.views.home.page_not_found'
