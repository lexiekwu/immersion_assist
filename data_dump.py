from a.third_party import cockroachdb as db
import pandas as pd

for table in ["users", "study_term", "learning_log", "daily_stats"]:
    rows = db.sql_query(f"SELECT * FROM {table}")
    df = pd.DataFrame(rows)
    df.to_csv(f"data_dumps/{table}.csv")
