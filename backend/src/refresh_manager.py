import sqlite3
from datetime import datetime, UTC
from db import get_db_connection


class RefreshManager:

    def __init__(self):
        self.conn = get_db_connection()

    def get_datasets(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM datasets")
        return cursor.fetchall()

    def record_refresh(
        self,
        dataset_name,
        status="SUCCESS",
        duration_ms=0,
        version="1.0",
        notes=""
    ):
        cursor = self.conn.cursor()

        refresh_time = datetime.now(UTC).isoformat()

        cursor.execute("""
        INSERT INTO dataset_refresh_history
        (
            dataset_name,
            refresh_time,
            refresh_status,
            refresh_duration_ms,
            version,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            dataset_name,
            refresh_time,
            status,
            duration_ms,
            version,
            notes
        ))

        self.conn.commit()

        return refresh_time

    def refresh_all(self):

        datasets = self.get_datasets()

        results = []

        for ds in datasets:

            dataset_name = ds["name"]

            refresh_time = self.record_refresh(
                dataset_name=dataset_name,
                status="SUCCESS",
                duration_ms=100,
                version=ds["version"],
                notes="Runtime refresh executed"
            )

            results.append({
                "dataset": dataset_name,
                "refresh_time": refresh_time,
                "status": "SUCCESS"
            })

        return results


    def record_failure(
        self,
        dataset_name,
        version="1.0",
        notes="Refresh failed"
    ):

        return self.record_refresh(
            dataset_name=dataset_name,
            status="FAILED",
            duration_ms=0,
            version=version,
            notes=notes
        )


if __name__ == "__main__":

    manager = RefreshManager()

    output = manager.refresh_all()

    print(output)


manager.record_failure(
    dataset_name="TEST_SOURCE",
    version="1.0",
    notes="Simulated failure"
)

print("Failure simulation recorded.")

cursor = manager.conn.cursor()

cursor.execute("""
SELECT * FROM dataset_refresh_history
""")

for row in cursor.fetchall():
    print(dict(row))