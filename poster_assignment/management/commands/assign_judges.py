import pandas as pd
from django.core.management.base import BaseCommand
import poster_assignment.models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

class Command(BaseCommand):
    help = "Assigns judges to posters based on expertise"

    def handle(self, *args, **kwargs):
        # Fetch all judges and their expertise
        judges = Judge.objects.all()
        judge_expertise = {
            judge.name: JudgeExpertise.objects.filter(judge=judge).values_list("keywords", flat=True)
            for judge in judges
        }

        # Fetch all posters
        posters = Poster.objects.all()

        # Preprocess expertise and abstracts
        judge_texts = {judge: " ".join(expertise) for judge, expertise in judge_expertise.items() if expertise}
        poster_texts = {poster: poster.abstract for poster in posters}

        # Use TF-IDF to compute similarity
        all_texts = list(judge_texts.values()) + list(poster_texts.values())
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        # Compute cosine similarity
        judge_vectors = tfidf_matrix[: len(judge_texts)]
        poster_vectors = tfidf_matrix[len(judge_texts) :]

        similarity_matrix = cosine_similarity(poster_vectors, judge_vectors)

        # Track judge assignments
        judge_assignment_count = defaultdict(int)
        max_assignments = 6  # Max posters per judge

        for i, poster in enumerate(posters):
            sorted_judges = sorted(
                enumerate(similarity_matrix[i]), key=lambda x: x[1], reverse=True
            )

            assigned_judges = []
            for j, score in sorted_judges:
                judge_name = list(judge_texts.keys())[j]
                judge = Judge.objects.get(name=judge_name)

                if judge_assignment_count[judge] < max_assignments:
                    assigned_judges.append(judge)
                    judge_assignment_count[judge] += 1

                if len(assigned_judges) == 2:  # Each poster gets 2 judges
                    break

            # Assign judges to poster
            poster.judges.set(assigned_judges)
            poster.save()

        self.stdout.write(self.style.SUCCESS("Successfully assigned judges to posters!"))
