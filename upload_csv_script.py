import pandas as pd
from datetime import datetime
import uuid
import time
import cockroachdb as db

CSV_PATH = "../flashcards.csv"
DRY_MODE = True
df = pd.read_csv(CSV_PATH)

# csv columns
# ,characters,english,pinyin,last_review_date_e2c,knowledge_factor_e2c,
# last_review_date_c2e,knowledge_factor_c2e,last_review_date_c2p,knowledge_factor_c2p

def _to_timestamp(dt):
    dt = datetime.strptime(
        dt, "%m/%d/%y"
    )
    return time.mktime(dt.timetuple())

def _insert_csv_row(row, dry_mode=DRY_MODE):
    card_id = uuid.uuid4()
    insert_term_sql = f"""
        UPSERT INTO study_term (id, term, translated_term, pronunciation)
        VALUES
            (
                '{card_id}',
                '{row.characters}',
                '{row.english}',
                '{row.pinyin}'
            )
    """
    insert_learning_log_sql = f"""
        UPSERT INTO learning_log (id, term_id, quiz_type, knowledge_factor, last_review)
        VALUES
            ('{uuid.uuid4()}', '{card_id}', 'pronunciation', {row.knowledge_factor_c2p}, {_to_timestamp(row.last_review_date_c2p)}),
            ('{uuid.uuid4()}', '{card_id}', 'reverse_translation', {row.knowledge_factor_e2c}, {_to_timestamp(row.last_review_date_e2c)}),
            ('{uuid.uuid4()}', '{card_id}', 'translation', {row.knowledge_factor_c2e}, {_to_timestamp(row.last_review_date_c2e)})
    """

    if dry_mode:
        print(insert_term_sql)
        print("\n\n")
        print(insert_learning_log_sql)

    else:
        db.sql_update_multi([insert_term_sql, insert_learning_log_sql])

for row in df.itertuples():
    _insert_csv_row(row)