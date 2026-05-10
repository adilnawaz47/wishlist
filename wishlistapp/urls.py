from django.urls import path
from . import views

urlpatterns = [
    path('', views.WishlistListView.as_view(), name='wishlist_list'),
    path('wishlist/<int:pk>/', views.WishlistDetailView.as_view(), name='wishlist_detail'),
    path('wishlist/create/', views.WishlistCreateView.as_view(), name='wishlist_create'),
    path('wishlist/<int:pk>/update/', views.WishlistUpdateView.as_view(), name='wishlist_update'),
    path('wishlist/<int:pk>/delete/', views.WishlistDeleteView.as_view(), name='wishlist_delete'),
    path('wishlist/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('memories/', views.MemoryListView.as_view(), name='memory_list'),
    path('memory/<int:pk>/', views.MemoryDetailView.as_view(), name='memory_detail'),
    path('memory/create/', views.MemoryCreateView.as_view(), name='memory_create'),
    path('memory/<int:pk>/update/', views.MemoryUpdateView.as_view(), name='memory_update'),
    path('memory/<int:pk>/delete/', views.MemoryDeleteView.as_view(), name='memory_delete'),
    path('create-admin/', views.create_admin),
]