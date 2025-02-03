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

@login_required
def image_create(request):
    if request.method == 'POST':
        print("✅ Received POST request")
        print("📂 request.FILES:", request.FILES)  # Debugging

        form = ImageCreateForm(request.POST, request.FILES)  # Include request.FILES

        if form.is_valid():
            print("✅ Form is valid")
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            print("✅ Image saved successfully:", new_image.image)
            messages.success(request, 'Image added successfully')
            return redirect('images:create')
        else:
            print("❌ Form errors:", form.errors)

    else:
        form = ImageCreateForm()

    return render(request, 'images/image/create.html', {'form': form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id = id, slug = slug)
    return render(request, 'images/image/image_detail.html', {'image': image})

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
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 10)
    page = request.GET.get('page')
    images_only = request.GET.get('image_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request, 'images/image/list_images.html', {'section':'images', 'image':images})
    return render(request, 'images/image/list.html', {'section':'images', 'images':images})

