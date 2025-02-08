import pandas as pd
from django.shortcuts import render
from .forms import UploadFileForm
from .models import Judge, JudgeExpertise, Poster

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
                judge, created = Judge.objects.update_or_create(
                    first_name=row["Judge FirstName"],
                    last_name=row["Judge LastName"],
                    defaults={
                        "department": row["Department"],
                        "hour_available": row["Hour available"],
                        "full_name": row["Full Name"],  # Store Full Name in model
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

