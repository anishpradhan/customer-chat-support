from django.shortcuts import render, get_object_or_404
from .forms import RoomForm, MessageForm
from .models import Room, Message, SupportGroup, UploadedFile
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import json
from tenants.models import Domain
from account.forms import RegistrationForm

# Create your views here.
User = get_user_model()

def index(request):
    # hostname = Domain.objects.get(tenant_id=request.user.tenant.id).domain
    # from django_tenants.utils import get_tenant_domain_model
    # domain_model = get_tenant_domain_model()
    # domain = domain_model.objects.select_related('tenant').get(domain=hostname)
    # try:
    #     tenant = domain.tenant
    # except domain_model.DoesNotExist:
    #     raise Http404('No tenant for hostname "%s"' % hostname)
    from django.db import connection
    connection.set_tenant(request.user.tenant)
    room_form = RoomForm(request.POST or None)
    if room_form.is_valid():
        room = room_form.save(commit=False)
        room.save()
        return HttpResponseRedirect(reverse('client_chat_page', args=[room.id]))

    context = {
        'room_form': room_form
    }
    return render(request, 'index.html', context=context)


def ajax_create_room(request):
    room_name = request.GET.get('room_name', None)
    support_group = request.GET.get('support', None)
    question = request.GET.get('question', None)
    support = SupportGroup.objects.get(name=support_group)
    room = Room(name=room_name, support_group=support, details=question)
    room.save()
    response = {
        'room_name': room.name,
        'room_id': str(room.id),
    }
    return JsonResponse(response)


def get_support_groups(request):
    support_group = SupportGroup.objects.all()
    names = [i.name for i in support_group]
    response = {
        'support_groups': names
    }
    return JsonResponse(response)


def join_chat(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.user.is_authenticated:
        user = User.objects.get(email=request.user.email)
        room.agents.add(user)
        message = Message()
        name = request.user.first_name or request.user.username
        message.message = '%s has joined the chat' % name
        room.messages.add(message, bulk=False)
    return HttpResponseRedirect(reverse('chatting:chat_page', args=[room.id]))


def end_chat(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    message = Message()
    name = request.user.first_name or request.user.username
    message.message = '%s has left the chat.  This chat has ended.' % name
    room.messages.add(message, bulk=False)
    # if request.POST.get('end_chat') == 'true':
    room.end()
    room.save()
    return HttpResponseRedirect(reverse('chatting:admin_index'))


def chat_page(request, room_id):
    room = Room.objects.get(id=room_id)
    if room.ended:
        return HttpResponseRedirect(reverse("chatting:admin_index"))
    messages = Message.objects.filter(room=room).order_by('sent')
    context = {
        'messages': messages,
        'room': room
    }
    return render(request, 'chat_page.html', context)


def client_chat_page(request, room_id):
    room = Room.objects.get(id=room_id)
    if room.ended:
        return HttpResponseRedirect(reverse("index"))
    messages = Message.objects.filter(room=room).order_by('sent')
    context = {
        'messages': messages,
        'room': room
    }
    return render(request, 'client_chat_page.html', context)


# ADMIN
def client_end_chat(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    message = Message()
    message.message = '%s has left the chat.  This chat has ended.' % room.name
    room.messages.add(message, bulk=False)
    # if request.POST.get('end_chat') == 'true':
    room.end()
    room.save()
    return HttpResponseRedirect(reverse('admin_index'))


# @login_required()
def admin_index(request):
    user = request.user
    all_chats = Room.objects.filter(agents=user)
    pending_rooms = Room.objects.filter(ended=None, agents=None).exclude(agents=user).order_by('-started')

    groups = SupportGroup.objects.filter(
        Q(supervisors=user) | Q(agents=user)
    )
    if groups:
        pending_rooms = pending_rooms.filter(support_group__in=groups)

    context = {
        'pending_rooms': pending_rooms,
        'all_chats': all_chats,
        'support_group': SupportGroup.objects.get(agents=user),
        'tenant_name': request.tenant.schema_name
        # 'urls': reverse('chat.views.join_chat', args=[pending_rooms.id])

    }
    if request.user.is_superuser:
        if request.POST:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()

                from django_tenants.utils import schema_context
                with schema_context('public'):
                    form = RegistrationForm(request.POST)
                    instance = form.save(commit=False)
                    instance.save()
            else:
                context['registration_form'] = form
        else:
            form = RegistrationForm(initial={
                'tenant': request.tenant,
            })
            context['registration_form'] = form

    return render(request, 'admin_index.html', context)


def get_last_10_messages(chatId):
    room = get_object_or_404(Room, id=chatId)
    return room.message.order_by('-sent').all()[:10]





# def get_user_contact(username):
#     # user = get_object_or_404(User, username=username)
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         user = None
#     return user
def get_user_contact(username, multitenant=False, schema_name=None):
    if multitenant:
        if not schema_name:
            raise AttributeError("Multitenancy support error: \
                scope does not have multitenancy details added. \
                did you forget to add ChatMTMiddlewareStack to your routing?")
        else:
            from django_tenants.utils import schema_context
            with schema_context(schema_name):
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = None
                return user
    else:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        return user


def get_current_chat(chatId):
    return get_object_or_404(Room, id=chatId)


def get_room(room_id, multitenant=False, schema_name=None):
    if multitenant:
        if not schema_name:
            raise AttributeError("Multitenancy support error: \
                    scope does not have multitenancy details added. \
                    did you forget to add ChatMTMiddlewareStack to your routing?")
        else:
            from django_tenants.utils import schema_context
            with schema_context(schema_name):
                return Room.objects.get(id=room_id)
    else:
        return Room.objects.get(id=room_id)


def get_file_by_id(file_id, multitenant=False, schema_name=None):
    if multitenant:
        if not schema_name:
            raise AttributeError("Multitenancy support error: \
                    scope does not have multitenancy details added. \
                    did you forget to add ChatMTMiddlewareStack to your routing?")
        else:
            from django_tenants.utils import schema_context
            with schema_context(schema_name):
                return UploadedFile.objects.get(id=file_id)
    else:
        return UploadedFile.objects.get(id=file_id)

# def save_file_message():
#     Message.objects.create()
