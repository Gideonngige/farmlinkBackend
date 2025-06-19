from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('question/', views.question, name='question'),
    path('get_questions/', views.get_questions, name='get_questions'),
    path('reply/', views.reply, name='reply'),
    path('get_replies/<int:question_id>/', views.get_replies, name='get_replies'),
    path('sell_product/', views.sell_product, name='sell_product'),
    path('get_products/<str:product_name>/', views.get_products, name='get_products'),
    path('buy/', views.buy, name='buy'),
    path('get_farmer_notifications/<int:farmer_id>/', views.get_farmer_notifications, name='get_farmer_notifications'),
    path('ask_question/<str:question>/', views.ask_question, name='ask_question'),
]