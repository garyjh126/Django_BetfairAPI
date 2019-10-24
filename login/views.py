from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Login, Market, Runner, SportsAPI
from .forms import LoginForm
from .tasks import timer_tick
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
import datetime
import requests
import pdb
import json
import threading
import time

from .api_logic.SportsAPI import *
from .api_logic.Form1 import *

sports_api = None

class LoginView(TemplateView):
    template_name = 'registration/login.html'
    logged_in_user = None 
    
    def get(self, request):
        self.form = LoginForm()
        return render(request, self.template_name, {'form': self.form })

    def post(self, request):
        self.form = LoginForm(request.POST)
        username_text = request.POST['username']
        password_text = request.POST['password']
        
        if self.form.is_valid(): # Django form validation already built in
            user = authenticate(request, username=username_text, password=password_text)
            if user is not None:
                self.logged_in_user = request.user
                username_text = self.form.cleaned_data['username']  # cleaned data refers to how the form data is sanitised (Prevents SQL injections)
                password_text = self.form.cleaned_data['password']
                self.form.log_betfair(username_text, password_text) # Call to betfair server
                login(request, user)
                return redirect('welcome')
            else: 
                html = "<html><body>There is a problem logging in <br> <a href='{% url 'login' %}'>login</a></body></html>"
                return HttpResponse(html)
        

        args = {'form': self.form, 'username_text': username_text, 'password_text' : password_text }
        return render(request, self.template_name, args)

class LogoutView(TemplateView):
    template_name = 'registration/logout.html'

    def get(self, request):
        logout(request)
        return render(request, 'registration/logout.html')

class RegistrationView(TemplateView):
    template_name = 'registration/register.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form })

    def post(self, request): 
        form = UserCreationForm(request.POST)
        if form.is_valid(): 
            form.save() # This is responsible for creating a new user
            return redirect('login')

class WelcomeUser(LoginView):
    template_name = 'registration/welcome_user.html'
    form = LoginForm()
    
    # def __init__(self):
    #     LoginView.__init__(self)
    #     self.sports_api = SportsAPI(self.form.payload, self.form.headers)

    def get(self, request):
        self.sports_api = SportsAPI_(self.form.payload, self.form.ssoid, self.form.headers)
        self.data_request()
        # timer_tick.delay(self.sports_api.model_instance.id)
        args = {'runners': 'dd' }
        return render(request, self.template_name, args)


    def data_request(self):
        # self.sports_api.send_sports_req({"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEventTypes", "params": {"filter":{}}, "id": 1})
        self.market_catalogue_req = MarketCatalogueRequest()
        self.form = Form(self.market_catalogue_req, self.market_catalogue_req.params, self.market_catalogue_req.params.filter.marketStartTime) 
        self.allMarkets = self.form.ListMarketCatalogue(self.sports_api)
        BuildListMarketBookRequests()
        # self.runners = Runner.objects.all()