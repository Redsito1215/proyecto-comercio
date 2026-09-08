from pymongo import DESCENDING


def ensure_report_indexes(db):
    db.report_runs.create_index([("created_at",DESCENDING)])
    db.report_exports.create_index([("created_at",DESCENDING)])
