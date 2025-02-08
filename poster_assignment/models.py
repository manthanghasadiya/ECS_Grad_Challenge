from django.db import models

class Judge(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=100)
    hour_available = models.CharField(
        max_length=10,
        choices=[("1", "Hour 1"), ("2", "Hour 2"), ("both", "Both Hours")],
    )
    max_assignments = models.IntegerField(default=6)
    current_assignments = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.department})"


class Poster(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    advisor_first_name = models.CharField(max_length=50)
    advisor_last_name = models.CharField(max_length=50)
    program = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class JudgeExpertise(models.Model):
    judge_name = models.CharField(max_length=200)  # Store name directly
    keywords = models.TextField(blank=True)  # Store expertise

    def __str__(self):
        return f"{self.judge_name} - {self.keywords}"


class Assignment(models.Model):
    poster = models.ForeignKey(Poster, on_delete=models.CASCADE)
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE)
    slot = models.CharField(max_length=10, choices=[("1", "Hour 1"), ("2", "Hour 2")])

    def __str__(self):
        return f"{self.poster.title} -> {self.judge.first_name} {self.judge.last_name}"
