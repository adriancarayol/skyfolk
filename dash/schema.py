import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from .models import DashboardEntry
from .base import (get_layout, )
from .utils import (
    get_user_plugins,
    get_workspaces,
    get_dashboard_settings,
    get_or_create_dashboard_settings
)
from django.http import Http404


class DashboardEntryType(DjangoObjectType):
    class Meta:
        model = DashboardEntry
        interfaces = (relay.Node,)


class Query(graphene.AbstractType):
    all_dashboard_entry = graphene.List(DashboardEntryType)

    def resolve_all_dashboard_entry(self, info, **kwargs):
        return DashboardEntry.objects.all()


class ModifyDashboardEntry(relay.ClientIDMutation):
    class Input:
        target_position = graphene.Int(required=True)
        source_position = graphene.Int(required=True)
        workspace = graphene.String(required=False)

    source = graphene.Field(DashboardEntryType)
    target = graphene.Field(DashboardEntryType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        target_position = input.get("target_position")
        source_position = input.get("source_position")
        workspace = input.get("workspace", None)

        if target_position == source_position:
            pass

        user = info.context.user

        registered_plugins = get_user_plugins(user)

        user_plugin_uids = [uid for uid, repr in registered_plugins]

        dashboard_settings = get_or_create_dashboard_settings(user)

        workspaces = get_workspaces(
            user,
            dashboard_settings.layout_uid,
            workspace,
            different_layouts=dashboard_settings.allow_different_layouts
        )

        layout = get_layout(
            layout_uid=(
                workspaces['current_workspace'].layout_uid
                if workspaces['current_workspace']
                else dashboard_settings.layout_uid
            ),
            as_instance=True
        )

        if workspaces['current_workspace_not_found']:
            raise Http404("Workspace does not exist")

        source = DashboardEntry.objects.filter(user=user,
                                           layout_uid=layout.uid, workspace=workspace,
                                           plugin_uid__in=user_plugin_uids,
                                           position=source_position).first()

        target = DashboardEntry.objects.filter(user=user,
                                           layout_uid=layout.uid,
                                           workspace=workspace,
                                           plugin_uid__in=user_plugin_uids,
                                           position=target_position).first()

        source.position = target_position
        target.position = source_position

        source.save(update_fields=['position'])
        target.save(update_fields=['position'])

        return ModifyDashboardEntry(source=source, target=target)


class Mutation(graphene.AbstractType):
    swap_dashboard_entry = ModifyDashboardEntry.Field()
