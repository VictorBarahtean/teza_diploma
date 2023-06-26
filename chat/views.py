from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from chat.models import Thread
from account.models import Contact
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils import formats


@login_required
def create_thread(request, username):
    user = User.objects.filter(username=username)[0]
    threads = Thread.objects.by_my_user(rq_user=request.user, user=user).prefetch_related('chatmessage_thread').order_by('timestamp')
    print(threads.count())
    if threads.count() == 0:
         Thread.objects.create(first_person=request.user, second_person=user)
    
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    
    '''list_of_threads = []
    thread_first = threads.first
    for thread in threads:
        print(thread.first_person.username, thread.second_person.username)
        print(user.username)
        if thread.second_person != user and thread.first_person != user:
            list_of_threads.append(thread)
        else:
            thread_first = thread
    list_of_threads.insert(0, thread_first)
    print(len(list_of_threads))'''
    #threads = Thread.objects.by_user(user=request.user).order_by('timestamp').prefetch_related('chatmessage_thread')
    
    context = {
        'section':'chat',
        'Threads': threads
    }
    #return render(request, 'messages.html', context)
    return redirect("chat:messages_page") 

@login_required
def messages_page(request,user=None):
    if user is None:
        threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    else:
        threads = Thread.objects.by_user(user=request.user).order_by('timestamp').prefetch_related('chatmessage_thread')
    #print(threads.count())
    '''users_threads = [thread.second_person for thread in threads]
    users_threads.remove(request.user)
    abonati = Contact.objects.filter(user_from=request.user)
    users_to = [user.user_to for user in abonati]
    abonati = Contact.objects.filter(user_to=request.user)
    users_all = [user.user_from for user in abonati] + users_to
    print(users_all)
    print(users_threads)
    for user in users_all:
        print("User:", user.username, "To user")
        if user not in users_threads and request.user not in users_threads:
            Thread.objects.create(first_person=request.user, second_person=user)
            #print("Create user")
    
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')'''

    context = {
        'section':'chat',
        'Threads': threads
    }
    return render(request, 'messages.html', context)

@require_POST
@login_required
def detail_usr(request):
    users_id = request.POST.get('user_id')
    thread_id = request.POST.get('thread_id')
    user = User.objects.filter(id=users_id)[0]
    thr_last = Thread.objects.filter(id=thread_id)[0]
    last_time = formats.date_format(thr_last.chatmessage_thread.order_by('-timestamp')[0].timestamp, "DATETIME_FORMAT")
    #print("TEST FUNC user_id:", users_id, last_time)
    return JsonResponse({'status':'ok', 'url_photo':user.profile.photo.url, 'last_time':last_time})

