import pandas as pd
import os


# ============================================================
# LOAD EXISTING RESOURCES
# ============================================================

RESOURCE_FILE = os.path.join(
    "dataset",
    "resources.csv"
)

if not os.path.exists(RESOURCE_FILE):

    print("ERROR: dataset/resources.csv was not found.")
    print("Make sure you are running this file from your project folder.")
    exit()


df = pd.read_csv(RESOURCE_FILE)

# Replace NaN with empty strings
df = df.fillna("")


# ============================================================
# VERIFIED DIRECT GITHUB REPOSITORIES
#
# IMPORTANT:
# We only put repositories here when they are actual
# GitHub repositories.
#
# GitHub topic/search pages are NOT used.
# ============================================================

VERIFIED_GITHUB = {

    "Student Performance Predictor":
        "https://github.com/naomilago/Student-Performance-Predictor",

    "Iris Flower Classification":
        "https://github.com/itzdineshx/Iris-flower-classification",

    "House Price Prediction":
        "https://github.com/katoss/house-price-prediction-project",

    "Movie Recommendation System":
        "https://github.com/dutta-sujoy/Movie-Recommendation-System",

    "Customer Churn Prediction":
        "https://github.com/YashrajThube/customer-churn-prediction",

    "Loan Approval Prediction":
        "https://github.com/ParthS007/Loan-Approval-Prediction",

    "Image Classification System":
        "https://github.com/sabar0401/Image_Classification_System",

    "Image Recognition App":
        "https://github.com/bhimrazy/Image-Recognition-App-using-FastAPI-and-PyTorch",

    "Simple Voice Assistant":
        "https://github.com/DDX-BiswaRanjan/Simple-Voice-Assistant",

    "Computer Vision System":
        "https://github.com/INSATEURO2026/Computer_vision",

    "Sentiment Analysis System":
        "https://github.com/baidu/Senta",

    "Face Detection Application":
        "https://github.com/Shreyaprasad21/Face-Detection-Applciation",

    "AI Assistant":
        "https://github.com/dicusa/AI-assistant",

    "AI Question Answering System":
        "https://github.com/geehaad/Question-Answering",

    "Student Data Analysis":
        "https://github.com/technologychannel/Student-Data-Analysis",

    "Data Cleaning Pipeline":
        "https://github.com/Developer-Sahil/data-cleaning-pipeline",

    "Sales Prediction System":
        "https://github.com/alanmaehara/Sales-Prediction",

    "Customer Insights Dashboard":
        "https://github.com/nicodatas/customer_insights_dashboard",

    "Fraud Detection System":
        "https://github.com/OlawumiSalaam/fraud-detection-system",

    "Portfolio Website":
        "https://github.com/codewithsadee/pfolio",

    "Learning Management System":
        "https://github.com/SMMousaviSP/lms",

    "Data Preprocessing":
        "https://github.com/MRamya-sri/Data-Preprocessing-ML"
}


# ============================================================
# VERIFIED DIRECT YOUTUBE PROJECT TUTORIALS
#
# IMPORTANT:
# We DO NOT guess YouTube IDs.
#
# If a project does not have a verified direct project video,
# its YouTube field stays empty.
# ============================================================

VERIFIED_PROJECT_YOUTUBE = {

    "Iris Flower Classification":
        "https://www.youtube.com/watch?v=BrFEmO-zPuA",

    "Loan Approval Prediction":
        "https://www.youtube.com/watch?v=EiSzb1oBCvY",

    "Portfolio Website":
        "https://www.youtube.com/watch?v=0YFrGy_mzjY"
}


# ============================================================
# COURSE PROJECT EXAMPLES
#
# Only direct GitHub repositories are allowed.
# GitHub /topics/ and /search URLs are removed.
# ============================================================

for index, row in df.iterrows():

    name = str(row["name"]).strip()
    resource_type = str(row["type"]).strip().lower()


    # ========================================================
    # PROJECT RESOURCES
    # ========================================================

    if resource_type == "project":

        # --------------------------------------------
        # REMOVE ALL OLD / UNVERIFIED YOUTUBE LINKS
        # --------------------------------------------

        df.at[index, "youtube_url"] = (
            VERIFIED_PROJECT_YOUTUBE.get(name, "")
        )


        # --------------------------------------------
        # PROJECTS DO NOT NEED COURSE LINKS
        # --------------------------------------------

        df.at[index, "free_course_url"] = ""

        df.at[index, "paid_course_url"] = ""


        # --------------------------------------------
        # ONLY VERIFIED DIRECT GITHUB REPOSITORIES
        # --------------------------------------------

        df.at[index, "project_url"] = (
            VERIFIED_GITHUB.get(name, "")
        )


    # ========================================================
    # COURSE RESOURCES
    # ========================================================

    elif resource_type == "course":

        old_project_url = str(
            row["project_url"]
        ).strip()


        # --------------------------------------------
        # REMOVE GITHUB SEARCH/TOPIC LINKS
        # --------------------------------------------

        if (
            "/topics/" in old_project_url
            or "/search" in old_project_url
        ):

            df.at[index, "project_url"] = (
                VERIFIED_GITHUB.get(name, "")
            )


        # --------------------------------------------
        # SAFETY CHECK
        # --------------------------------------------

        project_url = str(
            df.at[index, "project_url"]
        ).strip()

        if (
            project_url
            and
            (
                "/topics/" in project_url
                or "/search" in project_url
            )
        ):

            df.at[index, "project_url"] = ""


# ============================================================
# DATA PREPROCESSING
# ============================================================

data_preprocessing_exists = (
    df["name"].astype(str).str.strip()
    == "Data Preprocessing"
).any()


if not data_preprocessing_exists:

    new_row = {

        "id": len(df) + 1,

        "name": "Data Preprocessing",

        "type": "course",

        "youtube_url":
            "https://www.youtube.com/watch?v=0tDA4sPdZ-4",

        "free_course_url":
            "https://scikit-learn.org/stable/auto_examples/preprocessing/index.html",

        "paid_course_url":
            "",

        "project_url":
            "https://github.com/MRamya-sri/Data-Preprocessing-ML"
    }

    df = pd.concat(
        [
            df,
            pd.DataFrame([new_row])
        ],
        ignore_index=True
    )


# ============================================================
# FINAL SAFETY CLEANUP
# ============================================================

for index, row in df.iterrows():

    # --------------------------------------------
    # NO YOUTUBE SEARCH URLS
    # --------------------------------------------

    youtube = str(
        row["youtube_url"]
    ).strip()

    if (
        "youtube.com/results" in youtube
        or "search_query=" in youtube
    ):

        df.at[index, "youtube_url"] = ""


    # --------------------------------------------
    # NO GITHUB SEARCH/TOPIC URLS
    # --------------------------------------------

    github = str(
        row["project_url"]
    ).strip()

    if (
        "/topics/" in github
        or "/search" in github
    ):

        df.at[index, "project_url"] = ""


# ============================================================
# SAVE FINAL CSV
# ============================================================

df.to_csv(
    RESOURCE_FILE,
    index=False,
    encoding="utf-8"
)


# ============================================================
# VALIDATION
# ============================================================

check = pd.read_csv(
    RESOURCE_FILE
).fillna("")


bad_youtube = check[
    check["youtube_url"].astype(str).str.contains(
        "youtube.com/results|search_query=",
        regex=True
    )
]


bad_github = check[
    check["project_url"].astype(str).str.contains(
        "/topics/|/search",
        regex=True
    )
]


project_rows = check[
    check["type"].astype(str).str.lower()
    == "project"
]


project_youtube_count = (
    project_rows["youtube_url"]
    .astype(str)
    .str.strip()
    .ne("")
    .sum()
)


project_github_count = (
    project_rows["project_url"]
    .astype(str)
    .str.strip()
    .ne("")
    .sum()
)


print()
print("=" * 60)
print("RESOURCES CSV FIXED SUCCESSFULLY")
print("=" * 60)

print(
    f"Total resources: {len(check)}"
)

print(
    f"Project resources: {len(project_rows)}"
)

print(
    f"Verified project YouTube links: "
    f"{project_youtube_count}"
)

print(
    f"Verified project GitHub links: "
    f"{project_github_count}"
)

print(
    f"Bad YouTube search URLs: "
    f"{len(bad_youtube)}"
)

print(
    f"Bad GitHub topic/search URLs: "
    f"{len(bad_github)}"
)

print()

if len(bad_youtube) == 0 and len(bad_github) == 0:

    print("ALL SAFETY CHECKS PASSED.")

else:

    print("WARNING: SOME INVALID LINKS REMAIN.")

print()
print(
    "dataset/resources.csv has been updated."
)
print("=" * 60)