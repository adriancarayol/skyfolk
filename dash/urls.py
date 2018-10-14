from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from .views import (
    add_dashboard_entry,
    edit_dashboard_entry,
    PublicWorkspacesAJAX,
    clone_dashboard_workspace,
    copy_dashboard_entry,
    create_dashboard_workspace,
    cut_dashboard_entry,
    dashboard,
    dashboard_workspaces,
    delete_dashboard_entry,
    delete_dashboard_workspace,
    edit_dashboard,
    # edit_dashboard_settings,
    edit_dashboard_workspace,
    paste_dashboard_entry,
    plugin_widgets,
    update_entry_info,
    public_dashboard,
)

from .contrib.plugins.service.views import RetrieveInfoForServicePin
from .contrib.plugins.poll.views import submit_poll_response

app_name = 'dash'

urlpatterns = [
    # Paste dashboard entry
    url(_(r'^entry/paste/(?P<placeholder_uid>[\w_]+)/'
          r'(?P<workspace>[\w_\-]+)/pos/(?P<position>\d+)/$'),
        view=paste_dashboard_entry,
        name='dash.paste_dashboard_entry'),
    url(_(r'^entry/paste/(?P<placeholder_uid>[\w_]+)/pos/(?P<position>\d+)/$'),
        view=paste_dashboard_entry,
        name='dash.paste_dashboard_entry'),

    # Cut dashboard entry
    url(_(r'^entry/cut/(?P<entry_id>\d+)/$'),
        view=cut_dashboard_entry,
        name='dash.cut_dashboard_entry'),

    # Copy dashboard entry
    url(_(r'^entry/copy/(?P<entry_id>\d+)/$'),
        view=copy_dashboard_entry,
        name='dash.copy_dashboard_entry'),

    # Add dashboard entry.
    url(_(r'^entry/add/(?P<placeholder_uid>[\w_]+)/(?P<plugin_uid>[\w_\-]+)/'
          r'ws/(?P<workspace>[\w_\-]+)/pos/(?P<position>\d+)/$'),
        view=add_dashboard_entry,
        name='dash.add_dashboard_entry'),
    url(_(r'^entry/add/(?P<placeholder_uid>[\w_]+)/(?P<plugin_uid>[\w_\-]+)/'
          r'ws/(?P<workspace>[\w_\-]+)/$'),
        view=add_dashboard_entry,
        name='dash.add_dashboard_entry'),
    url(_(r'^entry/add/(?P<placeholder_uid>[\w_]+)/(?P<plugin_uid>[\w_\-]+)/'
          r'pos/(?P<position>\d+)/$'),
        view=add_dashboard_entry,
        name='dash.add_dashboard_entry'),
    url(_(r'^entry/add/(?P<placeholder_uid>[\w_]+)/'
          r'(?P<plugin_uid>[\w_\-]+)/$'),
        view=add_dashboard_entry,
        name='dash.add_dashboard_entry'),

    # Edit dashboard entry.
    url(_(r'^entry/edit/(?P<entry_id>\d+)/$'),
        view=edit_dashboard_entry,
        name='dash.edit_dashboard_entry'),

    # Delete dashboard entry.
    url(_(r'^entry/delete/(?P<entry_id>\d+)/$'),
        view=delete_dashboard_entry,
        name='dash.delete_dashboard_entry'),

    # ***************************************************************
    # ********************** Edit dashboard *************************
    # ***************************************************************
    # Edit dashboard.
    url(_(r'^edit/(?P<workspace>[\w_\-]+)/$'),
        view=edit_dashboard,
        name='dash.edit_dashboard'),
    url(_(r'^edit/$'),
        view=edit_dashboard,
        name='dash.edit_dashboard'),

    # ***************************************************************
    # ********************** Widgets for dashboard entries **********
    # ***************************************************************
    url(_(r'^plugin-widgets/(?P<placeholder_uid>[\w_]+)/'
          r'(?P<workspace>[\w_\-]+)/pos/(?P<position>\d+)/$'),
        view=plugin_widgets,
        name='dash.plugin_widgets'),
    # Workspace should not be named `pos`. Add check. TODO.
    url(_(r'^plugin-widgets/(?P<placeholder_uid>[\w_]+)/pos/'
          r'(?P<position>\d+)/$'),
        view=plugin_widgets,
        name='dash.plugin_widgets'),
    url(_(r'^plugin-widgets/(?P<placeholder_uid>[\w_]+)/'
          r'(?P<workspace>[\w_\-]+)/$'),
        view=plugin_widgets,
        name='dash.plugin_widgets'),
    url(_(r'^plugin-widgets/(?P<placeholder_uid>[\w_]+)/$'),
        view=plugin_widgets,
        name='dash.plugin_widgets'),
    url(_(r'^plugin-widgets/(?P<placeholder_uid>[\w_]+)/$'),
        view=plugin_widgets,
        name='dash.widgets'),

    # ***************************************************************
    # ********************** Dashboard workspace ********************
    # ***************************************************************
    # List workspaces.
    url(_(r'^workspaces/(?P<workspace>[\w_\-]+)/$'),
        view=dashboard_workspaces,
        name='dash.dashboard_workspaces'),

    url(_(r'^workspaces/$'),
        view=dashboard_workspaces,
        name='dash.dashboard_workspaces'),

    # Create dashboard workspace.
    url(_(r'^workspace/create/$'),
        view=create_dashboard_workspace,
        name='dash.create_dashboard_workspace'),

    # Edit dashboard workspace.
    url(_(r'^workspace/edit/(?P<workspace_id>\d+)/$'),
        view=edit_dashboard_workspace,
        name='dash.edit_dashboard_workspace'),

    # Delete dashboard workspace.
    url(_(r'^workspace/delete/(?P<workspace_id>\d+)/$'),
        view=delete_dashboard_workspace,
        name='dash.delete_dashboard_workspace'),

    # Clone dashboard workspace.
    url(_(r'^workspace/clone/(?P<workspace_id>\d+)/$'),
        view=clone_dashboard_workspace,
        name='dash.clone_dashboard_workspace'),

    # View dashboard workspace.
    url(_(r'^workspace/(?P<workspace>[\w_\-]+)/$'),
        view=dashboard,
        name='dash.dashboard'),

    # Edit dashboard settings.
    # url(_(r'^settings/edit/$'),
    #     view=edit_dashboard_settings,
    #     name='dash.edit_dashboard_settings'),

    # Update dashboard entry
    url(_(r'^entry/update/$'),
        view=update_entry_info,
        name='dash.update_dashobard_entry'),

    url(_(r'^entry/poll/response/$'),
        view=submit_poll_response,
        name='dash.response_dashboard_entry'),

    # public dashboard
    url(r'^(?P<username>[\w-]+)/(?P<workspace>[\w_\-]+)/$',
        view=public_dashboard,
        name='dash.public_dashboard'),

    url(r'^public/workspaces/(?P<user_id>\d+)/$',
        view=PublicWorkspacesAJAX.as_view(),
        name='dash.public_dashboard_workspaces'),
    
    # Service pin
    url(r'^pin/service/(?P<pin_id>\d+)/$',
        view=RetrieveInfoForServicePin.as_view(),
        name='dash.pin-service'),
]
