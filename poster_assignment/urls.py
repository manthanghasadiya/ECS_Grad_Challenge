from django.urls import path
from .views import home, upload_judges, upload_posters, upload_judge_expertise, assign

urlpatterns = [
    path("", home, name="home"),
    path("upload_judges/", upload_judges, name="upload_judges"),
    path("upload_posters/", upload_posters, name="upload_posters"),
    path("upload_judge_expertise/", upload_judge_expertise, name="upload_judge_expertise"),
    path("assign/", assign, name="assign"),
]
