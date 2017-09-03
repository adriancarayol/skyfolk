from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from badgify.models import Award
from django.contrib.auth.models import User
from django.http import Http404
from user_profile.models import NodeProfile
from django.http import HttpResponseForbidden


class UserAwards(APIView):

	renderer_classes = [TemplateHTMLRenderer]
	template_name  = "awards/my-awards.html"

	
	def get(self, request, *args, **kwargs):
		user_id = kwargs.pop('user_id', None)
		print('user_id: {}'.format(user_id))
		if not user_id:
			raise Http404

		try:
			profile = NodeProfile.nodes.get(user_id=user_id)
			request_user = NodeProfile.nodes.get(user_id=request.user.id)
		except User.DoesNotExist:
			raise Http404

		privacity = profile.is_visible(request_user)
		if privacity and privacity != 'all':
			return HttpResponseForbidden

		queryset = Award.objects.filter(user_id=profile.user_id)

		return Response({'awards': queryset})