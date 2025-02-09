# 🖼️ Poster Assignment System


A powerful web-based Poster Assignment System that streamlines the process of assigning judges to posters for academic or professional events, scoring the posters, and generating rankings. Built using Django, this system incorporates TF-IDF-based text similarity, automated email notifications, and responsive UI design for a seamless user experience.


--------


## 🚀 Features


### Admin Panel


+ Upload judge details (names, departments, available hours).
+ Upload poster details (titles, abstracts, advisors).
+ Automatically assign judges to posters based on expertise (using TF-IDF similarity).
+ Generate a final ranking table based on judges' scores.


### Judges Panel


+ Login securely with randomly generated passwords.
+ View assigned posters.
+ Score posters on innovation, implementation, and creativity.
+ Submit scores with a simple and user-friendly interface.


### Ranking and Scoreboard

+ Automatically calculate total scores and resolve ties using:
  + Innovation score (as the first tiebreaker).
  + Implementation score (as the second tiebreaker).
+ Display a leaderboard with responsive design for desktop and mobile.


## 🛠️ Tech Stack


### Backend
+ Django (Python framework)
+ SQLite (default database, easily replaceable with PostgreSQL/MySQL)

### Frontend
+ HTML5, CSS3
+ JavaScript (Dynamic dropdowns, confirmation popups)
+ Responsive design using custom CSS themes.

### Libraries and Tools
+ Pandas (data processing for CSV uploads)
+ Scikit-learn (TF-IDF vectorization)
+ NLTK (text tokenization and stopword removal)
+ Django Email Backend (automated emails)


## 📋 Installation

### Prerequisites

+ Python 3.8+
+ Django 4.0+
+ Virtualenv (optional but recommended)

### Steps

1. Clone the repository:

```
git clone https://github.com/your-username/poster-assignment-system.git

cd poster-assignment-system
```

2. Create a virtual environment:

```
python -m venv env

source env/bin/activate  # On Windows, use `env\Scripts\activate`
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Apply migrations:

```
python manage.py migrate
```

5. Start the server:

```
python manage.py runserver
```

6. Access the system at http://127.0.0.1:8000.


## 🔑 Usage

### Admin Workflow
+ Navigate to the admin panel (/admin).
+ Upload judge details and poster details using the upload pages.
+ Click the "Assign" button to automatically assign judges to posters based on expertise.
+ Use the "Final Scoreboard" button to view the leaderboard after scores are submitted.

### Judges Workflow

+ Login with your credentials (received via email).
+ View your assigned posters.
+ Submit scores for each poster based on:
  + Innovation
  + Implementation
  + Creativity
+  Logout once all scores are submitted.


## 📊 Ranking System
+ **Total Score** = (Sum of all scores) ÷ 6
+ **Tiebreaker Rules**:
  1. Higher **Innovation Score** wins.
  2. If tied, a higher **Implementation Score** wins.


## 🧑‍💻 Contributing

Feel free to submit pull requests or raise issues if you have suggestions for improvement.
