import json

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DeleteView
from neomodel import db

from user_groups.configuration.forms import ConfigurationGroupForm
from user_groups.models import UserGroups
from user_groups.node_models import NodeGroup
from user_profile.node_models import TagProfile


class ConfigurationGroupProfile(UpdateView):
    form_class = ConfigurationGroupForm
    template_name = 'groups/configuration/group_profile_config.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            group = UserGroups.objects.get(pk=self.kwargs.get('pk'))
        except UserGroups.DoesNotExist:
            raise Http404
        if group.owner_id != request.user.id:
            return HttpResponseForbidden()
        return super(ConfigurationGroupProfile, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(UserGroups, pk=self.kwargs.get('pk'))

    def get_initial(self):
        return {'tags': ','.join(
            [tag.title for tag in NodeGroup.nodes.get(group_id=self.object.group_ptr_id).interest.match()]),
            'is_public': not self.object.is_public}

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        user = self.request.user
        form = self.get_form()

        if self.object.owner_id != user.id:
            return HttpResponseForbidden("No tienes permisos para modificar este grupo.")

        if form.is_valid():
            return self.form_valid(form=form)

        return self.form_invalid(form=form)

    def form_valid(self, form, msg=None):
        data = {
            'response': False
        }
        if self.request.is_ajax():
            tags = form.cleaned_data.get('tags', None)
            try:
                g = NodeGroup.nodes.get(group_id=self.object.group_ptr_id)
            except NodeGroup.DoesNotExist:
                raise Http404
            try:
                with transaction.atomic(using="default"):
                    with db.transaction:
                        self.object = form.save()
                        if tags:
                            for tag in tags:
                                interest = TagProfile.nodes.get_or_none(title=tag)
                                if not interest:
                                    interest = TagProfile(title=tag).save()
                                if interest:
                                    g.interest.connect(interest)
                data['response'] = True
            except Exception:
                data['response'] = False

            return JsonResponse(data)
        return super(ConfigurationGroupProfile, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return HttpResponseBadRequest(json.dumps(form.errors),
                                          mimetype="application/json")
        return super(ConfigurationGroupProfile, self).form_invalid(form)


class DeleteGroup(DeleteView):
    http_method_names = ['post', 'get', ]
    template_name = 'groups/configuration/group_delete.html'
    model = UserGroups

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            group = UserGroups.objects.get(pk=self.kwargs.get('pk'))
        except UserGroups.DoesNotExist:
            raise Http404
        if group.owner_id != request.user.id:
            return HttpResponseForbidden()
        return super(DeleteGroup, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(UserGroups, pk=self.kwargs.pop('pk'))

    def delete(self, request, *args, **kwargs):
        user = request.user

        self.object = self.get_object()

        if self.object.owner_id != user.id:
            return HttpResponseForbidden()

        try:
            self.object.delete()
        except IntegrityError:
            return redirect('user_groups:configuration:configuration_delete_group', pk=self.object.pk)

        return redirect('user_groups:list-group')
