from django.urls import path

from . import views

urlpatterns=[
    path("ide/",views.ide,name="ide"),
    path("ide/runcode/",views.runcode,name="runcode"),
]