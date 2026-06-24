from datetime import datetime, UTC
from db import get_db_connection


class SourceHealthService:

    def __init__(self):
        self.conn = get_db_connection()

    def get_dataset_health(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            dataset_name,
            MAX(refresh_time) AS last_refresh
        FROM dataset_refresh_history
        GROUP BY dataset_name
        """)

        rows = cursor.fetchall()

        health_report = []

        for row in rows:

            dataset_name = row["dataset_name"]
            last_refresh = row["last_refresh"]

            from datetime import datetime, UTC

            refresh_dt = datetime.fromisoformat(
                last_refresh.replace("Z", "+00:00")
            )

            age_hours = (
                datetime.now(UTC) - refresh_dt
            ).total_seconds() / 3600

            if age_hours <= 24:
                freshness_score = 100
                health_status = "HEALTHY"
                confidence_impact = 0

            elif age_hours <= 72:
                freshness_score = 80
                health_status = "WARNING"
                confidence_impact = 10

            elif age_hours <= 168:
                freshness_score = 60
                health_status = "WARNING"
                confidence_impact = 25

            else:
                freshness_score = 20
                health_status = "STALE"
                confidence_impact = 50

            health_report.append({
                "dataset": dataset_name,
                "last_refresh": last_refresh,
                "freshness_score": freshness_score,
                "health_status": health_status,
                "confidence_impact": confidence_impact,
                "source_reachable": True
            })

        return health_report


if __name__ == "__main__":

    service = SourceHealthService()

    report = service.get_dataset_health()

    for item in report:
        print(item)