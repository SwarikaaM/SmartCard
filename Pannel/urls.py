from django.urls import path
from .views import pannel,changemode
urlpatterns = [
    path("",pannel,name="pannelget"),
    path("changemode/",changemode,name="changemode"),
]
