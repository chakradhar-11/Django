from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static 
from pmax.views import home,signup,login,dashboard,logout,movie_detail,book_show

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home,name="home"),
    path('signup/',signup,name="signup"),
    path('login/',login,name="login"),
    path('dashboard/',dashboard,name="dashboard"),
    path('logout/',logout,name="logout"),
    path('movie_detail/<int:movie_id>/',movie_detail,name="movie_detail"),
    path("book_show/<int:show_id>/",book_show,name="book_show")
    
]

urlpatterns=urlpatterns+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)