import graphene
from django.db import transaction
from graphene import relay
from graphene_django.types import DjangoObjectType
from .models import DashboardEntry, DashboardWorkspace
from .base import get_layout
from .utils import (
    get_user_plugins,
    get_workspaces,
    get_dashboard_settings,
    get_or_create_dashboard_settings,
)
from django.http import Http404


class DashboardWorkspaceType(DjangoObjectType):
    class Meta:
        model = DashboardWorkspace


class DashboardEntryType(DjangoObjectType):
    workspace = graphene.Field(
        DashboardWorkspaceType, id=graphene.Int(), slug=graphene.String()
    )

    def resolve_workspace(self, args, context, info):
        id = args.get("id")
        slug = args.get("slug")

        if id is not None:
            return DashboardWorkspace.objects.get(pk=id)

        if slug is not None:
            return DashboardWorkspace.objects.get(slug=slug)

        return None

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
        workspace_name = graphene.String(required=False)

    source = graphene.Field(DashboardEntryType)
    target = graphene.Field(DashboardEntryType)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        target_position = input.get("target_position")
        source_position = input.get("source_position")
        workspace = input.get("workspace_name", None)
        source, target = cls.swap_widgets(
            info, source_position, target_position, workspace
        )

        return ModifyDashboardEntry(source=source, target=target)

    @classmethod
    def swap_widgets(cls, info, source_position, target_position, workspace):
        user = info.context.user

        if not user.is_authenticated:
            return None, None

        if target_position == source_position:
            return None, None

        registered_plugins = get_user_plugins(user)
        user_plugin_uids = [uid for uid, repr in registered_plugins]
        dashboard_settings = get_or_create_dashboard_settings(user)

        workspaces = get_workspaces(
            user,
            dashboard_settings.layout_uid,
            workspace,
            different_layouts=dashboard_settings.allow_different_layouts,
        )

        layout = get_layout(
            layout_uid=(
                workspaces["current_workspace"].layout_uid
                if workspaces["current_workspace"]
                else dashboard_settings.layout_uid
            ),
            as_instance=True,
        )

        if workspaces["current_workspace_not_found"]:
            raise Http404("Workspace does not exist")

        if workspace:
            source = DashboardEntry.objects.filter(
                user=user,
                workspace__slug=workspace,
                layout_uid=layout.uid,
                plugin_uid__in=user_plugin_uids,
                position=source_position,
            ).first()
            target = DashboardEntry.objects.filter(
                user=user,
                layout_uid=layout.uid,
                workspace__slug=workspace,
                plugin_uid__in=user_plugin_uids,
                position=target_position,
            ).first()
        else:
            source = DashboardEntry.objects.filter(
                user=user,
                layout_uid=layout.uid,
                plugin_uid__in=user_plugin_uids,
                position=source_position,
            ).first()

            target = DashboardEntry.objects.filter(
                user=user,
                layout_uid=layout.uid,
                plugin_uid__in=user_plugin_uids,
                position=target_position,
            ).first()

        source_saved = False
        target_save = False

        if source and not target:
            source.position = target_position
            source_saved = True
        elif target and not source:
            target.position = source_position
            target_save = True
        elif source and target:
            source.position = target_position
            target.position = source_position
            source_saved, target_save = True, True

        try:
            with transaction.atomic():
                if source_saved:
                    source.save(update_fields=["position"])
                if target_save:
                    target.save(update_fields=["position"])
        except Exception as e:
            pass

        return source, target


class Mutation(graphene.AbstractType):
    swap_dashboard_entry = ModifyDashboardEntry.Field()
