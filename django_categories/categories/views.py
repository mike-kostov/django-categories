from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import requires_csrf_token, csrf_protect
from .models import Category
from .forms import CategoryForm

# Create your views here.
def index(request):
    template = loader.get_template('categories.html')
    categories = Category.objects.all()
    return HttpResponse(template.render({'categories': categories}))

def indexByDepth(request, depth=0):
    template = loader.get_template('categories.html')
    categories = Category.objects.filter(depth=depth)
    return HttpResponse(template.render({'categories': categories, 'depth': depth}))

def show(request, category_id):
    return HttpResponse(f'Here I imagine this category id {category_id}')

@csrf_protect
@require_GET
def create(request):
    template = loader.get_template('categoryForm.html')
    return render(request, 'categoryForm.html', {
        'form': CategoryForm(),
        'formUrl': reverse('categories.store'),
    })

@requires_csrf_token
@require_POST
def store(request):
    form = CategoryForm(request.POST)
    form.is_valid()
    parent = form.cleaned_data['parent']
    depth = 0
    while parent:
        parent = parent.parent
        depth += 1
    form.instance.depth = depth
    new_category = form.save()
    return HttpResponse(new_category.name + ' ' + str(new_category.depth))


@csrf_protect
@require_GET
def edit(request, category_id):
    category = Category.objects.get(id=category_id)
    form = CategoryForm(instance=category)
    return render(request, 'categoryForm.html', {
        'form': form,
        'formUrl': reverse('categories.update', args=(category_id,)),
    })

@requires_csrf_token
@require_POST
def update(request, category_id):
    category = Category.objects.get(id=category_id)
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
        depth = 0
        parent = form.cleaned_data['parent']
        while parent:
            parent = parent.parent
            depth += 1
        form.instance.depth = depth
        form.save()
        return HttpResponse(f'Category updated successfully {category.id} {category.name}')
    return HttpResponse('Category update failed')
