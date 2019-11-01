from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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
import pickle
from .test import timer_tick_test


from .api_logic.SportsAPI import *
from .api_logic.Form1 import Form_

sports_api = None


class LoginView(TemplateView):
    template_name = 'registration/login.html'
    logged_in_user = None

    def get(self, request):
        self.form = LoginForm()
        return render(request, self.template_name, {'form': self.form})

    def post(self, request):
        self.form = LoginForm(request.POST)
        username_text = request.POST['username']
        password_text = request.POST['password']

        if self.form.is_valid():  # Django form validation already built in
            user = authenticate(
                request, username=username_text, password=password_text)
            if user is not None:
                self.logged_in_user = request.user
                # cleaned data refers to how the form data is sanitised (Prevents SQL injections)
                username_text = self.form.cleaned_data['username']
                password_text = self.form.cleaned_data['password']
                # Call to betfair server
                self.form.log_betfair(username_text, password_text)
                login(request, user)
                return redirect('welcome')
            else:
                html = "<html><body>There is a problem logging in <br> <a href='{% url 'login' %}'>login</a></body></html>"
                return HttpResponse(html)

        args = {'form': self.form, 'username_text': username_text,
                'password_text': password_text}
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
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # This is responsible for creating a new user
            return redirect('login')


class WelcomeUser(LoginView):
    template_name = 'registration/welcome_user.html'
    form = LoginForm()
    print("welcome")
    # def __init__(self):
    #     LoginView.__init__(self)
    #     self.sports_api = SportsAPI(self.form.payload, self.form.headers)

    def get(self, request):
        self.sports_api = SportsAPI_(
            self.form.payload, self.form.ssoid, self.form.headers)
        self.data_request()
        # self.my_pickle(Form_.marketDictionary, Form_.runnerDictionary)

        # timer_tick.delay(Form_.bookRequestList)
        timer_tick_test(Form_.bookRequestList)
        args = {'runners':  self.runners}
        return render(request, self.template_name, args)

    def data_request(self):
        # self.sports_api.send_sports_req({"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEventTypes", "params": {"filter":{}}, "id": 1})
        self.market_catalogue_req = MarketCatalogueRequest()
        self.form = Form_(self.market_catalogue_req, self.market_catalogue_req.params,
                          self.market_catalogue_req.params.filter.marketStartTime)
        allMarkets = self.form.ListMarketCatalogue(self.sports_api)
        self.form.BuildListMarketBookRequests()
        self.runners = Runner.objects.all()


@login_required
def profile(self, request):
    args = {'runners':  self.runners}
    return render(request, self.template_name, args)
