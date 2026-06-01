import sqlite3

conn = sqlite3.connect('instance/tether.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("Database Tables:")
print("=" * 60)
for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print(f"  {'Column':20} {'Type':15} {'Nullable'}")
    print(f"  {'-'*20} {'-'*15} {'-'*8}")
    for col in columns:
        nullable = "NO" if col[3] else "YES"
        print(f"  {col[1]:20} {col[2]:15} {nullable}")

conn.close()
print("\n" + "=" * 60)
print("✓ Database schema verification complete")
