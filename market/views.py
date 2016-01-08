from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='accounts/login')
def market_inicio(request):
	return render(request,'account/skyfolk_store.html')
