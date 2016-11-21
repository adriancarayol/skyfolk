from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from .models import UserGroups
from django.contrib.auth.decorators import login_required
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .forms import FormUserGroup
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

class UserGroupCreate(AjaxableResponseMixin, CreateView):
    model = UserGroups
    form_class = FormUserGroup
    http_method_names = [u'post']
    success_url = '/thanks/'

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        owner = get_object_or_404(get_user_model(),
                                    pk=request.POST['owner'])

        # Comprobamos si somos el mismo usuario
        if self.request.user.pk != owner.pk:
            raise IntegrityError()

        print('POST DATA: {}'.format(request.POST))
        print('tipo emitter: {}'.format(type(owner)))
        if form.is_valid():
            print('IS VALID')
            try:
                group = form.save(commit=False)
                group.owner = owner
                group.save()
                # Without this next line the tags won't be saved.
                form.save_m2m()
                print('GROUP CREATED!')
            except IntegrityError as e:
                print("views.py line 30 -> {}".format(e))
            return self.form_valid(form=form)

        print(form.errors)
        return self.form_invalid(form=form)

user_group_create = login_required(UserGroupCreate.as_view(), login_url='/')


class UserGroupList(ListView):

    model = UserGroups
    template_name = "groups/list_group.html"

group_list = login_required(UserGroupList.as_view(), login_url='/')