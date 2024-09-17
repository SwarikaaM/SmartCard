from django.shortcuts import render, redirect
import requests
import json
import time
from .forms import ModeForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

api_key = "16f7d522edbb1a7b98914ac3d5d7335a43c094443e47b17e5e3f9c471f7afa5e"
remote_esp = "192.168.1.110"

def getMode():
    timeout_value = 5
    time.sleep(0.1)
    try:
        r = requests.get(f"http://{remote_esp}/get", headers={"apikey": api_key}, timeout=timeout_value)
        return r.json()
    except requests.exceptions.ConnectTimeout:
        return JsonResponse({"Mode": "servre down"})
    except requests.exceptions.ConnectionError:
        return JsonResponse({"Mode": "servre error"})
    except requests.exceptions.ReadTimeout:
        return JsonResponse({"Mode": "servre error"})


@staff_member_required
def pannel(request):
    data = getMode()["Mode"]
    form = ModeForm({"mode": "reader", "aadharno": "12039", "panno": "2032"})
    ctx = {
        "form": form,
        "Mode": data,
    }
    return render(request, "Pannel/pannel.html", ctx)


def changemode(request):
    try:
        if request.method == "GET":
            return "not found"

        if request.method == "POST":
            mode = request.POST.get('mode')
            ano = request.POST.get('aadharno')
            pno = request.POST.get('panno')
            r = requests.post(f"http://{remote_esp}/set",
                              headers={"apikey": api_key},
                              params={
                                  "value": mode,
                                  "aadharno": ano,
                                  "panno": pno
                              })
            time.sleep(0.1)
    except requests.exceptions.ConnectionError as error:
        return JsonResponse({"Mode": "servre error"})
    except requests.ReadTimeout:
        return JsonResponse({"Mode": "servre error"})
    return redirect("pannelget")
