import json
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import requires_csrf_token, csrf_protect
from collections import defaultdict

from .graph_service import CategoryGraphService
from .models import Category, CategorySimilarity
from .forms import CategoryForm

# graph_service = CategoryGraphService()

# Create your views here.
def index(request):
    template = loader.get_template('categories.html')
    categories = Category.objects.all().prefetch_related('children')
    return HttpResponse(template.render({'categories': categories}))

def indexByDepth(request, depth=0):
    template = loader.get_template('categories.html')
    categories = Category.objects.filter(depth=depth).prefetch_related('children')
    return HttpResponse(template.render({'categories': categories, 'depth': depth}))

def indexByParent(request, parent_id=0):
    template = loader.get_template('categories.html')
    categories = Category.objects.filter(parent_id=parent_id).prefetch_related('children')
    return HttpResponse(template.render({'categories': categories, 'parent_id': parent_id}))

def getRabbitHole(request, start, end):
    graph_service = CategoryGraphService()
    path_ids = graph_service.find_shortest_path(start, end)

    if path_ids is None:
        return HttpResponse(json.dumps({
            "start_id": start,
            "end_id": end,
            "length": 0,
            "path": [],
        }), content_type="application/json")

    path_details = Category.objects.filter(id__in=path_ids).in_bulk(path_ids)
    path_sequence = [{"id": pid, "name": path_details[pid].name} for pid in path_ids]

    return HttpResponse(json.dumps({
        "start_id": start,
        "end_id": end,
        "length": len(path_ids) - 1,
        "path": path_sequence,
    }), content_type="application/json")

def getRabbitIslands(request):
    graph_service = CategoryGraphService()
    islands = graph_service.get_rabbit_islands()

    island_data = []
    for island in islands:
        category_details = Category.objects.filter(id__in=island).values('id', 'name')
        island_data.append({
            "size": len(island),
            "categories": list(category_details)
        })

    template = loader.get_template('islands.html')
    return HttpResponse(template.render({
        "total_islands": len(islands),
        "islands": island_data
    }))

    # adjacency_list = defaultdict(list)
    # all_category_ids = set(Category.objects.values_list('id', flat=True))
    # similarities = CategorySimilarity.objects.all().values_list(
    #     'category_a_id', 'category_b_id'
    # )
    #
    # for id_a, id_b in similarities:
    #     adjacency_list[id_a].append(id_b)
    #     adjacency_list[id_b].append(id_a)
    #
    # for cat_id in all_category_ids:
    #     if cat_id not in adjacency_list:
    #         adjacency_list[cat_id] = []
    #
    # visited = set()
    # islands = []
    #
    # for start_node in all_category_ids:
    #     if start_node not in visited:
    #         island = []
    #         stack = [start_node]
    #
    #         while stack:
    #             current_node = stack.pop()
    #             if current_node not in visited:
    #                 visited.add(current_node)
    #                 island.append(current_node)
    #
    #                 for neighbor in adjacency_list.get(current_node, []):
    #                     stack.append(neighbor)
    #         if island:
    #             islands.append(island)
    #
    # template = loader.get_template('islands.html')
    # island_data = [];
    # for island in islands:
    #     category_details = Category.objects.filter(pk__in=island).values('id', 'name')
    #
    #     island_data.append({
    #         'size': len(island),
    #         'categories': list(category_details)
    #     })
    # # categories = Category.objects.filter(pk__in=islands).prefetch_related('children')
    # return HttpResponse(template.render({
    #     'total_islands': len(islands),
    #     'islands': island_data,
    # }))

def getLongestRabbitHole(request):
    """
    GET /categories/getLongestRabbitHole/
    Returns the longest shortest path (graph diameter approximation).
    """
    graph_service = CategoryGraphService()
    path_ids = graph_service.find_longest_rabbit_hole()

    # Fetch category names/details for a friendly response
    path_details = Category.objects.filter(id__in=path_ids).in_bulk(path_ids)
    path_sequence = [{"id": pid, "name": path_details[pid].name} for pid in path_ids]

    return HttpResponse(json.dumps({
        "length": len(path_ids) - 1,
        "path": path_sequence,
        "message": "Calculated via two-BFS approximation on the largest connected component."
    }))

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
        form.save()
        return HttpResponse(f'Category updated successfully {category.id} {category.name}')
    return HttpResponse('Category update failed')
