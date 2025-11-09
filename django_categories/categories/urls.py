from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.index, name='categories.index'),
    path('categoriesByDepth/<int:depth>/', views.indexByDepth, name='categories.indexByDepth'),
    path('categoriesByParent/<int:parent_id>/', views.indexByParent, name='categories.indexByParent'),
    path('categories/create/', views.create, name='categories.create'),
    path('categories/store/', views.store, name='categories.store'),
    path('categories/<int:category_id>/', views.show, name='categories.show'),
    path('categories/<int:category_id>/edit', views.edit, name='categories.edit'),
    path('categories/<int:category_id>/update', views.update, name='categories.update'),
]
