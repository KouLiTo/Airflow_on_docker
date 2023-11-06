from airflow.decorators import dag, task
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
import sqlite3
import os
import pendulum
import requests
import xmltodict


PODCAST_URL = "https://www.marketplace.org/feed/podcast/marketplace/"
EPISODE_FOLDER = "episodes"
FRAME_RATE = 16000
DB_FILE = "saved_podcasts.db"
DB_PATH = os.path.join(os.path.dirname(os.getcwd()), "podcast_summary", DB_FILE)


@dag(
    dag_id="project_dags",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2023, 11, 4),
    catchup=False,
)
def project_dags():

    create_db = SqliteOperator(
        task_id="create_sqlite_table",
        sqlite_conn_id="my_sql_connection",
        sql="""
                CREATE TABLE IF NOT EXISTS episodes(
                link TEXT PRIMARY KEY,
                title TEXT,
                filename TEXT,
                published TEXT,
                description TEXT
                )
                """
    )

    @task
    def get_episodes():
        print("Start")
        data = requests.get(PODCAST_URL)
        feed = xmltodict.parse(data.text)

        # # individual podcasts episodes that are released daily
        episodes = feed["rss"]["channel"]["item"]
        print(f"{len(episodes)} episodes found, but only first five will be returned")

        # # let us return just five episodes
        return episodes[:5]

    podcast_episodes = get_episodes()
    create_db >> podcast_episodes
    # create_db.set_downstream(podcast_episodes)


summary = project_dags()
