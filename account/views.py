from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, SearchForm
from .models import Profile, Contact
from django.contrib.auth.models import User
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.views.decorators.http import require_POST
from bookmarks.common.decorators import ajax_required
from actions.utils import create_action
from actions.models import Action
from datetime import datetime, timedelta


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login or password')
    else:
        form = LoginForm()
    
    return render(request, 'account/login.html', {'form': form})


#@login_required
def dashboard(request):
    if request.user.is_authenticated:
        if request.user.profile.photo == '':
            redirect('edit')
        
        #actions = Action.objects.exclude(user=request.user)
        actions = Action.objects
        following_ids = request.user.following.values_list('id', flat=True)
        following_ids = following_ids.exclude(id=request.user.id)
        date_last_days = datetime.now().date() - timedelta(days=7)
        #print(date_last_days)

        query = f'''
            SELECT id, user_id, verb, target_ct_id, target_id, max(created)
            FROM actions_action
            WHERE user_id != '{request.user.id}'
            AND verb == 'is following'
            AND target_id = '{request.user.id}'
            AND created >= '{date_last_days}'
            GROUP BY user_id, verb, target_ct_id, target_id
            ORDER BY id desc, created desc
        '''
        new_followers = actions.raw(query)
 
        query = f'''
            SELECT id, user_id, verb, target_ct_id, target_id, max(created)
            FROM actions_action
            WHERE user_id != '{request.user.id}'
            AND verb != 'has created an account'
            AND user_id in ({",".join([str(x) for x in list(following_ids)])})
            GROUP BY user_id, verb, target_ct_id, target_id
            ORDER BY created desc
        '''
        actions = actions.raw(query)
        actions.new_followers = [user_id.id for user_id in new_followers]

        '''if following_ids:
            actions = actions.filter(user_id__in=following_ids)
        else:
            actions = actions.select_related('user', 'user__profile')\
                        .prefetch_related('target')'''


        return render(request, 'account/dashboard.html', {'section':'dashboard', 'actions':actions, 'new_followers':new_followers})
    else:
        return render(request, 'welcPage.html')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request, 'account/register_done.html', {'new_user':new_user})
    else:
        user_form = UserRegistrationForm()
        
    return render(request, 'account/register.html', {'user_form':user_form})

@login_required
def edit(request):
    message_status = ''
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            #messages.success(request, 'Profile updated successfully')
            message_status = "Profilul a fost modificat cu success"
        else:
            #messages.error(request, 'Error updating your profile')
            message_status = "Eroare la modificarea profilului"
        
        user_form = request.user
        profile_form = request.user.profile
        profile_form.date_of_birth_mod = datetime.strftime(datetime.strptime(str(profile_form.date_of_brith), "%Y-%m-%d"), "%Y-%m-%d")
    else:
        user_form = request.user
        profile_form = request.user.profile
        profile_form.date_of_birth_mod = datetime.strftime(datetime.strptime(str(profile_form.date_of_brith), "%Y-%m-%d"), "%Y-%m-%d")
    
    return render(request, 'account/edit.html', {'user_form':user_form, 'profile_form':profile_form, 'message_status':message_status})

@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'account/user/list.html', {'section':'people', 'users':users, 'filt':'all'})

@login_required
def followers_list(request):
    abonati = Contact.objects.filter(user_to=request.user)
    users = [user.user_from for user in abonati]
    return render(request,'account/user/list.html', {'section':'people', 'users':users, 'filt':'follow'})

@login_required
def followed_list(request):
    abonati = Contact.objects.filter(user_from=request.user)
    users = [user.user_to for user in abonati]
    return render(request,'account/user/list.html', {'section':'people', 'users':users, 'filt':'folled'})

@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    
    user.abonari = Contact.objects.filter(user_from=user).count()

    query = f'''
        SELECT id, user_id, verb, target_ct_id, target_id, max(created)
        FROM actions_action
        WHERE user_id = '{user.id}'
        AND verb != 'has created an account'
        GROUP BY user_id, verb, target_ct_id, target_id
        ORDER BY created desc
    '''
    user.actions_user = Action.objects.raw(query)
    #print(user.profile.date_of_brith)
    #print((datetime.now() - datetime.strptime(str(user.profile.date_of_brith), "%Y-%d-%m")).days)
    try:
        user.age_result = (datetime.now() - datetime.strptime(str(user.profile.date_of_brith), "%Y-%m-%d")).days // 365
    except:
        user.age_result = "-"


    return render(request, 'account/user/detail.html', {'section':'people', 'user':user})


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()

            return JsonResponse({'status':'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status':'ok'})
    
    return JsonResponse({'status':'ok'})

@login_required
def search_user1(request):
    users = request.POST.get('users')
    filt = request.POST.get('filt')
    
    search_value = request.POST.get('search_value')
    if filt != "all":
        abonati = Contact.objects.filter(user_from=request.user)
        users = [user.user_to for user in abonati]
        users = [user for user in users if str(user.get_full_name()).lower().__contains__(str(search_value).lower())]
    else:
        users = User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name__icontains=search_value)
    #print(users)
    #context = {'section':'people', 'users': users, 'filt':filt}
    return render(request, 'account/user/list.html', {'section':'people', 'users': users, 'filt':filt})


@login_required
def search_user(request):
    form = SearchForm(request.POST)
    if form.is_valid():
        search_value = form.cleaned_data['search_query']
        filt = form.cleaned_data['type_search']
        print("Search value:", str(search_value).strip(), "Filt:", filt)
        if filt != "all":
            if filt == "follow":
                abonati = Contact.objects.filter(user_to=request.user)
                users_list = [user.user_from for user in abonati]
            else:
                abonati = Contact.objects.filter(user_from=request.user)
                users_list = [user.user_to for user in abonati]

            if str(search_value).strip() != '':
                users = [user for user in users_list if str(user.get_full_name()).lower().__contains__(str(search_value).lower())]
            else:
                users = users_list
        else:
            if str(search_value).strip() != '':
                users = User.objects.annotate(full_name=Concat('first_name', V(' '), 'last_name')).filter(full_name__icontains=search_value)
            else:
                users = User.objects.filter(is_active=True)

        return render(request, 'account/user/list.html', {'section':'people', 'users': users, 'filt':filt, 'srch_val':search_value})

    context = {'form': form, 'users': None, 'filt':'all'}

    
    return render(request, 'account/user/list.html', context)



