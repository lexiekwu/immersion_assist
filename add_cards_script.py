#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime
from study_term import StudyTerm
import uuid

print(f"""
Add terms 1 at a time:
characters, pinyin, english
type 'q' when done.
""")


def split_term(term):
    parts = term.split(" ")
    characters = parts[0]
    i = 1
    while (
        i < len(parts) and
        len(parts[i]) > 1 and
        parts[i][0].isalpha() and
        parts[i][-1].isnumeric()
    ):
        i += 1
    pinyin = " ".join(parts[1:i])
    english = " ".join(parts[i:])
    return characters, pinyin, english

term = input()
rows_to_add = []

while term != 'q':
    characters, pinyin, english = split_term(term)
    StudyTerm(
        uuid.uuid4(),
        characters,
        english,
        pinyin
    )._save()
    term = input()