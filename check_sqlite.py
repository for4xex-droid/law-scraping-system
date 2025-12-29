import sqlite3


def check_sqlite_laws():
    conn = sqlite3.connect("welfare_laws_v3.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT law_full_name, count(*) FROM laws JOIN articles ON laws.law_id = articles.law_id GROUP BY law_full_name"
    )
    rows = cursor.fetchall()

    with open("sqlite_report.txt", "w", encoding="utf-8") as f:
        f.write("\n=== SQLite Registered Laws ===\n")
        found = False
        for name, count in rows:
            f.write(f"{name}: {count} articles\n")
            if "障害者虐待" in name:
                found = True

        if not found:
            f.write("\n❌ 障害者虐待防止法 is MISSING in SQLite!\n")
        else:
            f.write("\n✅ 障害者虐待防止法 is Present in SQLite.\n")
    print("Check sqlite_report.txt")

    conn.close()


if __name__ == "__main__":
    check_sqlite_laws()
