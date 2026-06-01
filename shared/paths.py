import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(PROJECT_ROOT, "apps")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
MASTER_KEYWORDS_DIR = os.path.join(DATA_DIR, "master_keywords")
COUNTRY_LANGUAGE_MAP_PATH = os.path.join(DATA_DIR, "google_play_country_language_map.xlsx")


def project_path(*parts):
    return os.path.join(PROJECT_ROOT, *parts)


def app_path(*parts):
    return os.path.join(APPS_DIR, *parts)
