# from importlib.metadata import pass_none

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm
from .models import Judge, JudgeExpertise, Poster, generate_random_password
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from difflib import SequenceMatcher
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm


from django.shortcuts import render

def home(request):
    """
    Render the homepage.
    """
    return render(request, "home.html")


def upload_judges(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            df = pd.read_excel(file, engine="openpyxl")
            # Ensure required columns are present
            required_columns = ["Judge FirstName", "Judge LastName", "Department", "Hour available"]
            for col in required_columns:
                if col not in df.columns:
                    return render(request, "upload.html", {"form": form, "error": f"Missing column: {col}"})

            # Fill NaNs and trim whitespace
            df.fillna("", inplace=True)
            df["Judge FirstName"] = df["Judge FirstName"].astype(str).str.strip()
            df["Judge LastName"] = df["Judge LastName"].astype(str).str.strip()

            # **Create Full Name Column**
            df["Full Name"] = df["Judge FirstName"] + " " + df["Judge LastName"]

            # Process each row
            for _, row in df.iterrows():
                password = generate_random_password(row["Judge FirstName"])
                judge, created = Judge.objects.update_or_create(
                    first_name=row["Judge FirstName"],
                    last_name=row["Judge LastName"],
                    defaults={
                        "department": row["Department"],
                        "hour_available": row["Hour available"],
                        "full_name": row["Full Name"],  # Store Full Name in model
                        "password": password
                    }
                )
            # for _, row in df.iterrows():
            #     judge, created = Judge.objects.get_or_create(
            #         first_name=row["Judge FirstName"],
            #         last_name=row["Judge LastName"],
            #         department=row["Department"],
            #         hour_available=row["Hour available"],
            #     )
                if "keywords" in row:
                    JudgeExpertise.objects.create(judge=judge, keywords=row["keywords"])

            return render(request, "upload_success.html")
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})


def upload_posters(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            df = pd.read_excel(file, engine="openpyxl")

            for _, row in df.iterrows():
                Poster.objects.create(
                    title=row["Title"],
                    abstract=row["Abstract"],
                    advisor_first_name=row["Advisor First Name"],
                    advisor_last_name=row["Advisor Last Name"],
                    program=row["Program"],
                )

            return render(request, "upload_success.html")
    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})


def upload_judge_expertise(request):
    """
    Uploads an Excel file and directly saves its contents to the JudgeExpertise table.
    """
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            df = pd.read_excel(file, engine="openpyxl")  # Read Excel file

            # Ensure required columns exist
            required_columns = ["Judge Name", "Keywords"]
            for col in required_columns:
                if col not in df.columns:
                    return render(request, "upload.html", {"form": form, "error": f"Missing column: {col}"})

            df.fillna("", inplace=True)  # Fill NaN values with empty strings

            # Directly insert all rows into the database
            JudgeExpertise.objects.bulk_create([
                JudgeExpertise(judge_name=row["Judge Name"].strip(), keywords=row["Keywords"].strip())
                for _, row in df.iterrows()
            ])

            return render(request, "upload_success.html")

    else:
        form = UploadFileForm()
    return render(request, "upload.html", {"form": form})

def assign(request):
    if request.method == "GET":
        poster = Poster.objects.all().values()
        exprts = JudgeExpertise.objects.all().values()
        jdj = Judge.objects.all().values()
        sample = pd.DataFrame.from_records(poster)
        detail_of_judge = pd.DataFrame.from_records(exprts)
        judge = pd.DataFrame.from_records(jdj)

        sample['name'] = sample['advisor_first_name'].str.strip() + " " + sample['advisor_last_name'].str.strip()
        judge['name'] = judge['first_name'].str.strip() + " " + judge['last_name'].str.strip()
        detail_of_judge['name'] = detail_of_judge['judge_name']
        def check_name_similarity(name1, name2):
            name1_words = set(name1.lower().split())
            name2_words = set(name2.lower().split())
            return len(name1_words & name2_words) >= 2

        judge['merge_key'] = judge['name'].apply(lambda x: [y for y in detail_of_judge['name'] if check_name_similarity(x, y)])
        judge = judge.drop(columns='name')
        # Explode the merge_key to have a row for each potential match
        judge_exploded = judge.explode('merge_key')
        judge_exploded.rename(columns={'merge_key': 'name'}, inplace=True)

        # Merge the datasets
        matched_df = pd.merge(judge_exploded, detail_of_judge, on='name', how='inner')
        matched_df['hour_available'] = matched_df['hour_available'].astype(str)

        # nltk.download('stopwords')
        # nltk.download('punkt')

        def preprocess(text):
            stop_words = set(stopwords.words('english'))
            tokens = word_tokenize(text)
            # Ensure only alphanumeric words are kept and stopwords are removed
            filtered_words = [word.lower() for word in tokens if word.isalnum() and word.lower() not in stop_words]
            return filtered_words

        def similarity(a, b):
            return SequenceMatcher(None, a, b).ratio()

        def calculate_tfidf_cosine_similarity(text1, text2):
            """
            Calculate the cosine similarity between two texts after converting to TF-IDF vectors.

            Args:
            text1 (str): The first text.
            text2 (str): The second text.

            Returns:
            float: Cosine similarity between the two TF-IDF vectors.
            """
            # Ensure input is appropriate for the vectorizer (needs to be string, not list of tokens)
            if isinstance(text1, list):
                text1 = ' '.join(text1)
            if isinstance(text2, list):
                text2 = ' '.join(text2)

            vectorizer = TfidfVectorizer()
            # Fit and transform the texts
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Calculate cosine similarity between the first and second document (indices 0 and 1)
            sim_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
            return sim_score[0][0]

        # Example usage of data; this should be replaced with actual data
        abstract = sample['abstract'][0]

        # Preprocess the abstract
        abstract_processed = preprocess(abstract)

        # Dictionary to hold similarity scores along with professor details
        similarity_scores = []

        poster_scores = {}
        for i, abstract in enumerate(sample['abstract']):
            abstract_processed = preprocess(abstract)
            poster_number = i + 1
            scores = []
            for index, expertise in enumerate(matched_df['keywords']):
                expertise_processed = preprocess(expertise)
                sim_score = calculate_tfidf_cosine_similarity(abstract_processed, expertise_processed) * 100
                # Include check for advisor
                if matched_df['name'][index] != sample['name'][i]:  # Ensure the judge is not the advisor
                    scores.append(
                        (matched_df['name'][index], sim_score, matched_df['hour_available'][index], poster_number))
            poster_scores[poster_number] = sorted(scores, key=lambda x: x[1], reverse=True)

        # Assign judges to posters, respecting the rules
        judge_limits = {name: 0 for name in matched_df['name']}
        assignments = {i: [] for i in range(1, len(sample['abstract']) + 1)}
        for poster, scores in poster_scores.items():
            assigned_judges = set()  # To keep track of judges already assigned to this poster
            for i in range(len(scores) - 1):

                if len(assignments[poster]) == 2:
                    break

                judge1, _, availability1, score1 = scores[i]
                judge2, _, availability2, score2 = scores[i + 1]

                # Determine the condition for the poster assignment based on its even or odd identifier
                is_even_poster = poster % 2 == 0
                valid_availability1 = availability1 in (['2', 'both'] if is_even_poster else ['1', 'both'])
                valid_availability2 = availability2 in (['2', 'both'] if is_even_poster else ['1', 'both'])

                # Function to try to assign a judge
                def try_assign(judge):
                    if judge not in assigned_judges and judge_limits[judge] < 6 and len(assignments[poster]) < 2:
                        assignments[poster].append(judge)
                        judge_limits[judge] += 1
                        assigned_judges.add(judge)
                        return True
                    return False

                # Assign judges based on the calculated conditions and scores
                if valid_availability1 in (['2'] if is_even_poster else ['1']):
                    if valid_availability1:
                        if try_assign(judge1):
                            continue  # Continue if judge1 is successfully assigned
                if valid_availability2 in (['2'] if is_even_poster else ['1']):
                    if valid_availability2 and abs(score1 - score2) < 1:
                        if try_assign(judge2):
                            continue  # Continue if judge2 is successfully assigned

                # In case neither judge is assigned and both are valid, prioritize by lower score
                if valid_availability1:
                    if try_assign(judge1):
                        continue

            judge, _, availability, score = scores[len(scores) - 1]

            # Determine the condition for the poster assignment based on its even or odd identifier
            is_even_poster = poster % 2 == 0
            valid_availability = availability in (['2', 'both'] if is_even_poster else ['1', 'both'])

            if valid_availability:
                if try_assign(judge):
                    continue

        # Output the assignments
        for poster, judges in assignments.items():
            hour = "Hour 1" if poster % 2 != 0 else "Hour 2"
            print(sample.loc[poster - 1]['title'])
            print(f"Poster {poster} ({hour}): Judged by {', '.join(judges)}")

        for poster_id, judges in assignments.items():
            if judges:
                try:
                    poster_obj = Poster.objects.get(title=sample.loc[poster_id - 1]['title'])
                    poster_obj.assigned_judge_1 = judges[0] if len(judges) > 0 else None
                    poster_obj.assigned_judge_2 = judges[1] if len(judges) > 1 else None
                    poster_obj.save()  # ✅ Save the assigned judges to the Poster model
                except Poster.DoesNotExist:
                    continue

    return render(request, "assignment.html")


def judge_login(request):
    return render(request, "login.html")

def login(request):
    if request.method == "POST":
        password = request.POST.get("password")
        # print(password)
        jdj = Judge.objects.get(password=password)
        pst = Poster.objects.all().values()
        posters = pd.DataFrame.from_records(pst)
        print(jdj.full_name)
        assigned_poster_titles = []
        if jdj:
            judge_name = jdj.full_name  # Use full_name for lookup

            # Find posters assigned to this judge
            assigned_posters = Poster.objects.filter(
                assigned_judge_1=judge_name
            ) | Poster.objects.filter(
                assigned_judge_2=judge_name
            )

            return render(request, "results.html", {"judge": jdj, "posters": assigned_posters})
        else:
            return render(request, "login.html")


def submit_scores(request):
    if request.method == "POST":
        judge_name = request.POST.get("judge_name")  # Get the logged-in judge's name
        posters = Poster.objects.all()  # Fetch all posters from the database

        for poster in posters:
            score_key = f"score_{poster.title}"  # Example: "score_5"

            # Check if this score is in the POST request
            if score_key in request.POST:
                score = request.POST[score_key]

                if score:  # If a score is provided
                    score = int(score)  # Convert to integer

                    # Determine if this judge is Judge 1 or Judge 2
                    if poster.assigned_judge_1 == judge_name:
                        poster.judge_1_score = score
                    elif poster.assigned_judge_2 == judge_name:
                        poster.judge_2_score = score

                    poster.save()  # Save the updated score to the database

        return redirect("home")  # Redirect to home page after submission

    return HttpResponse("Invalid request", status=400)

# def results(request):
#     return render(request, "results.html")
