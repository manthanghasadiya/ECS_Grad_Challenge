from django.urls import path
from .views import home, upload_judges, upload_posters, upload_judge_expertise, assign, login, judge_login, submit_scores

urlpatterns = [
    path("", home, name="home"),
    path("upload_judges/", upload_judges, name="upload_judges"),
    path("upload_posters/", upload_posters, name="upload_posters"),
    path("upload_judge_expertise/", upload_judge_expertise, name="upload_judge_expertise"),
    path("assign/", assign, name="assign"),
    path("login/", login, name="login"),
    path("judge_login/", judge_login, name="judge_login"),
    path("submit_scores/", submit_scores, name="submit_scores"),
]
