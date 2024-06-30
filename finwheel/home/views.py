from django.shortcuts import render
from home.utils import *
from bank.models import *
# Create your views here.
def index(request):
    if request.user.is_authenticated:
        xt = verify_setup(request.user)
        if xt[0] == False:
            return render(request, "home/logged_index.html",{
                "setup":xt,
            })
        else:
            return render(request, "home/logged_index.html",{
                "setup":xt,
                "bank_info": CashAccount.objects.get(for_user=request.user)
            })
    else:
        return render(request, "home/index.html")