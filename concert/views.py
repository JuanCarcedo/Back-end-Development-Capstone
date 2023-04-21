from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


# Create your views here.

def signup(request):
    context: dict = {"form": SignUpForm}

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.filter(username=username).first()
            
            if not user:
                user = User.objects.create(username=username, password=make_password(password))
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            
            else:
                context['message'] = "User already exists."
        
        except User.DoesNotExist:
            pass

    return render(request, "signup.html", context)


def index(request):
    return render(request, "index.html")


def songs(request):
    songs_url = "http://songs-sn-labs-carcedojuan.labs-prod-openshift-san-a45631dc5778dc6371c67d206ba9ae5c-0000.us-east.containers.appdomain.cloud"
    songs = req.get(f"{songs_url}/song").json()
    return render(request, "songs.html", {"songs": songs})


def photos(request):
    photos_url = "https://pictures.11iu4fdk72t2.us-south.codeengine.appdomain.cloud"
    photos = req.get(f"{photos_url}/picture").json()
    return render(request, "photos.html", {"photos": photos})


def login_view(request):
    context: dict = {"form": LoginForm}

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

    return render(request, "login.html", context)


def logout_view(request):
    logout(request)

    return HttpResponseRedirect(reverse("index"))


def concerts(request):

    if request.user.is_authenticated:
        list_of_concerts: list = []
        concert_objects = Concert.objects.all()
        
        for concert in concert_objects:
            try:
                status = item.attendee.filter(user=request.user).first().attending
            
            except:
                status = "-"
            
            list_of_concerts.append({
                "concert": concert,
                "status": status
            })
        
        return render(request, "concerts.html", {"concerts": list_of_concerts})
    
    return HttpResponseRedirect(reverse("login"))


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = Concert.objects.get(pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
