from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import T_KANZYA

@login_required
def index(request):

    KanzyaData = T_KANZYA.objects.all()

    return render(request, "YoyakuKanri/YoyakuKanri.html", {"kanzyadatas": KanzyaData})
