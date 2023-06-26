from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm, ImageUpdateForm
from .models import Image
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from bookmarks.common.decorators import ajax_required, is_ajax
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action
from django.conf import settings
import redis

r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, password=settings.REDIS_PASSWORD)

def get_views_image(images):
    for ind, image in enumerate(images):
        try:
            images[ind].views = int(r.get(f"image:{str(image.id)}:views"))
        except:
            images[ind].views = 0
    
    return images


@login_required
def image_create(request):
    if request.method == 'POST':
        #form = ImageCreateForm(data=request.POST)
        form = ImageCreateForm(request.POST, request.FILES)
        print('img cr')

        if form.is_valid():
            print('valid')
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)

            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)
        
    return render(request, 'images/image/create.html', {'section':'images', 'form':form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)

    #print("Image visibility", image.visibility )
    if image.visibility == "for_non":
        return redirect('dashboard')

    total_views = r.incr('image:{}:views'.format(image.id))
    r.zincrby('image_ranking', image.id, 1)

    return render(request, 'images/image/detail.html', {'section':'images', 'image':image, 'total_views':total_views})

@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    print(image_id)
    action = request.POST.get('action')
    print(action)

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_likes.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_likes.remove(request.user)
            
            total_likes = image.users_likes.count()
            return JsonResponse({'status':'ok', 'image_id':image_id, 'action':action, 'total_likes':total_likes})
        except:
            pass
    return JsonResponse({'status':'ok', 'image_id': image_id, 'action':action, 'total_likes':0})

@login_required
def image_list(request):
    images = Image.objects.filter(visibility__in=["for_all", "for_fol"])
    paginator = Paginator(images, 8)
    page = request.GET.get('page')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Daca prima pagina nu este numar returnam prima pagina 
        image = paginator.page(1)
    except EmptyPage:
        if is_ajax(request=request):
            # Daca primi AJAX-request cu numarul de pagini mai mare dechit totalul paginilor
            # returnam pagina goala
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)

    images = get_views_image(images)
    #images = images.order_by("views")
    images = sorted(images, key= lambda t: t.views, reverse=True)
    #print(images_test)
    if is_ajax(request=request):
        return render(request, 'images/image/list_ajax.html', {'section':'images', 'images':images})
    
    return render(request, 'images/image/list.html', {'section':'images', 'images':images})


@login_required
def image_ranking(request):
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html', {'section':'images', 'most_viewed':most_viewed})

@ajax_required
@login_required
@require_POST
def option_image(request):
    option = request.POST.get('option')
    image_id = request.POST.get('id')

    if option == "visibility":
        value = request.POST.get('value')
        Image.objects.filter(id=image_id).update(visibility=value)
    elif option == "delete_feed":
        Image.objects.filter(id=image_id).update(visibility='for_non')

    return JsonResponse({'status':'ok'})

@login_required
def image_edit(request, id=None):
    message_status = ''
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        visibility = request.POST.get('visibility')
        slug = request.POST.get('slug')

        if image_id != None:
            #image_form.save()
            Image.objects.filter(id=image_id).update(title=title, description=description, visibility=visibility)
            #message_status = "Postarea a fost modificat cu success"
            return redirect("images:detail", id=id, slug=slug)
        else:
            #messages.error(request, 'Error updating your profile')
            message_status = "Eroare la modificarea postării"
            print("Eroare la modificarea postării")
            #messages.error(request, 'Eroare la modificarea postării')
            image_form = Image.objects.filter(id=id)[0]

    else:
        image_form = Image.objects.filter(id=id)[0]
        #profile_form.date_of_birth_mod = datetime.strftime(datetime.strptime(str(profile_form.date_of_brith), "%Y-%m-%d"), "%Y-%m-%d")
    
    return render(request, 'images/image/edit.html', {'image_form':image_form, 'message_status':message_status})
