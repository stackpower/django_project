from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from Option_Trading import settings
#from django.conf import settings
from django.shortcuts import redirect
from django.views.static import serve

urlpatterns = [
    #url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_URL}),
    #url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_URL}),
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name='login'),
    url(r'^login_account/$', views.login_account, name='login_account'),
    url(r'^dashboard/(?P<id>\w+)$', views.dashboard, name='dashboard'),
    url(r'^admin_dashboard/(?P<id>\w+)$', views.admin_dashboard, name='admin_dashboard'),
    url(r'^admin_user_setting/$', views.admin_user_setting, name='admin_user_setting'),
    url(r'^admin_account_setting/$', views.admin_account_setting, name='admin_account_setting'),
    url(r'^account_setting/$', views.account_setting, name='account_setting'),
    url(r'^account_info_update/(?P<id>\w+)$', views.account_info_update, name='account_info_update'),
    url(r'^add_user/$', views.add_user, name='add_user'),
    url(r'^get_user_info/$', views.get_user_info, name='get_user_info'),
    url(r'^update_user/$', views.update_user, name='update_user'),
    url(r'^add_security/$', views.add_security, name='add_security'),
    url(r'^get_security_info/$', views.get_security_info, name='get_security_info'),
    url(r'^update_security/$', views.update_security, name='update_security'),
    url(r'^update_security_ticker/$', views.update_security_ticker, name='update_security_ticker'),
    url(r'^delete_security/(?P<id>\w+)$', views.delete_security, name='delete_security'),
    url(r'^percentile_filter/$', views.percentile_filter, name='percentile_filter'),
    url(r'^symbol_detail_graph/$', views.symbol_detail_graph, name='symbol_detail_graph'),
    url(r'^add_journal_watch/$', views.add_journal_watch, name='add_journal_watch'),
    url(r'^add_symbol_to_watchlist/$', views.add_symbol_to_watchlist, name='add_symbol_to_watchlist'),
    url(r'^view_journal_watchlist/$', views.view_journal_watchlist, name='view_journal_watchlist'),
    url(r'^delete_journal_watchlist/$', views.delete_journal_watchlist, name='delete_journal_watchlist'),
    url(r'^view_journal_watch_graph/$', views.view_journal_watch_graph, name='view_journal_watch_graph'),
    url(r'^view_journal_past_graph/$', views.view_journal_past_graph, name='view_journal_past_graph'),
    url(r'^delete_journal_item/$', views.delete_journal_item, name='delete_journal_item'),
    url(r'^get_movement_chart/$', views.get_movement_chart, name='get_movement_chart'),
    url(r'^get_earningsfly/$', views.get_earningsfly, name='get_earningsfly'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # uploaded media
    urlpatterns += static(settings.TEMPLATES_URL, document_root=settings.TEMPLATES_ROOT)