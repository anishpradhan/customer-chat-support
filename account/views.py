from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationForm
from .forms import AccountAuthenticationForm
from .models import Account
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponseRedirect
import json


def registration_view(request, tenant_name):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            # connection.set_schema_to_public()
            # form.save()
            # connection.set_tenant(form.)
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('account:login')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    context['tenant_name'] = request.tenant
    return render(request, 'register.html', context)


def logout_view(request):
    logout(request)
    return redirect('/')


def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        # return redirect("account:index")
        return HttpResponseRedirect(reverse("chatting:admin_index"))
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                request.session['tenant_uuid'] = str(user.tenant.tenant_uuid)
                # from django_tenants.utils import schema_context
                # with schema_context(user.tenant):
                #     login(request, user)
                #     request.session['tenant_uuid'] = str(user.tenant.tenant_uuid)

                # request.session['tenant_uuid'] = str(user.tenant.tenant_uuid)
                # request.session['user'] = json.dumps(list(user.values()))

                print("TENANT UUID:", request.session['tenant_uuid'])
                return redirect(reverse("account:index"))
                # return HttpResponseRedirect(reverse("chatting:admin_index"))
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'login.html', context)


# @login_required()
def index(request):
    print('INDEX:', request.user)
    return redirect(reverse("chatting:admin_index"))
    # users = Account.objects.all()
    # context = {
    #     'users': users,
    #     'tenant': request.tenant
    # }
    # if request.user.is_superuser:
    #     if request.POST:
    #         form = RegistrationForm(request.POST)
    #         if form.is_valid():
    #             instance = form.save(commit=False)
    #             instance.save()
    #
    #             from django_tenants.utils import schema_context
    #             with schema_context('public'):
    #                 form = RegistrationForm(request.POST)
    #                 instance = form.save(commit=False)
    #                 instance.save()
    #
    #             email = form.cleaned_data.get('email')
    #             raw_password = form.cleaned_data.get('password1')
    #             account = authenticate(email=email, password=raw_password)
    #             login(request, account)
    #             return redirect('account:index')
    #         else:
    #             context['registration_form'] = form
    #     else:
    #         form = RegistrationForm(initial={
    #             'tenant': request.tenant,
    #         })
    #         context['registration_form'] = form
    #
    # return render(request, 'index_a.html', context=context)
