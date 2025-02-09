import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


def generate_random_password(first_name):
    """Generate a password in the format: FirstName + Random 4 Characters"""
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return f"{first_name[:4]}{random_chars}"


class Judge(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=100)
    hour_available = models.CharField(
        max_length=10,
        choices=[("1", "Hour 1"), ("2", "Hour 2"), ("both", "Both Hours")],
    )
    password = models.CharField(max_length=12,blank=True, null=True)  # 🔹 Auto-generated password
    max_assignments = models.IntegerField(default=6)
    current_assignments = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        """Generate a unique password only when creating a new judge."""
        if not self.password:  # Only generate if password is empty
            self.password = generate_random_password(self.first_name)
        super().save(*args, **kwargs)  # Call Django's save method

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.department})"


class Poster(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    advisor_first_name = models.CharField(max_length=50)
    advisor_last_name = models.CharField(max_length=50)
    program = models.CharField(max_length=100)

    assigned_judge_1 = models.CharField(max_length=200, blank=True, null=True)
    assigned_judge_2 = models.CharField(max_length=200, blank=True, null=True)

    # judge_1_score = models.IntegerField(blank=True, null=True)
    # judge_2_score = models.IntegerField(blank=True, null=True)

    judge_1_innovation = models.IntegerField(blank=True, null=True)
    judge_1_implementation = models.IntegerField(blank=True, null=True)
    judge_1_creativity = models.IntegerField(blank=True, null=True)

    # Scores for Judge 2
    judge_2_innovation = models.IntegerField(blank=True, null=True)
    judge_2_implementation = models.IntegerField(blank=True, null=True)
    judge_2_creativity = models.IntegerField(blank=True, null=True)

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
