from itertools import count
import redis
from django.conf import settings

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from actions.utils import create_action

from django.db.models import Count
@login_required
def image_create(request):
    if request.method == 'POST':
        print("Received POST request")
        print("request.FILES:", request.FILES)  # Debugging

        form = ImageCreateForm(request.POST, request.FILES)  # Include request.FILES

        if form.is_valid():
            print("Form is valid")
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked_image', new_image)
            messages.success(request, 'Image added successfully')
            return redirect('images:create')
        else:
            print("Form errors:", form.errors)

    else:
        form = ImageCreateForm()

    return render(request, 'images/image/create.html', {'form': form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id = id, slug = slug)
    total_views = r.incr(f'image:{image.id}:views')
    r.zincrby('image_ranking', 1, image.id)
    return render(request, 'images/image/image_detail.html',
    {'section':'images',
     'image': image,
     'total_views': total_views
     })

@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id = image_id)
            if action == 'like':
                image.user_like.add(request.user)
                create_action(request.user, 'liked_image', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .models import Image

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 10)
    page = request.GET.get('page')
    images_only = request.GET.get('image_only')
    #images_by_popularity = Image.objects.annotate(like=count('users_like')).order_by('-likes')
    #images_by_popularity = Image.objects.order_by('-total_likes')
    images = paginator.get_page(page)

    if images_only:
        if not images:
            return HttpResponse('No more images.', status=204)
        return render(request, 'images/image/list_images.html', {'section': 'images', 'images': images})

    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})

@login_required
def image_ranking(request):
    image_ranking = r.zrevrange('image_ranking', 0, 9, withscores=True)
    image_ranking_ids = [int(id) for id in image_ranking]
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images', 'most_viewed': most_viewed}
    )
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)