from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='accounts/login')
def market_inicio(request):
	return render(request,'account/skyfolk_store.html')
