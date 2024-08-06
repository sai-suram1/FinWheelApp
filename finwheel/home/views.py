from django.http import HttpResponseRedirect
from django.shortcuts import render
import home.utils
from bank.models import *
from django.urls import reverse
# Create your views here.
def index(request):
    if request.user.is_authenticated:
        xt = home.utils.verify_setup(request.user)
        if xt[0] == False:
            return render(request, "home/logged_index.html",{
                "setup":xt,
            })
        elif xt[0] == True and xt[1] == True:
            return HttpResponseRedirect(reverse("bank:investments"))
        else:
            return render(request, "home/logged_index.html",{
                "setup":xt,
                "bank_info": CashAccount.objects.get(for_user=request.user)
            })
    else:
        return render(request, "home/index.html")