"""Inspect and print the complete database schema for MargNetra backend."""

import asyncio
from sqlalchemy import inspect
from app.db.session import engine


async def print_schema():
    async with engine.connect() as conn:
        def get_schema(sync_conn):
            inspector = inspect(sync_conn)
            table_names = sorted(inspector.get_table_names())
            return {
                table: {
                    "columns": inspector.get_columns(table),
                    "pks": inspector.get_pk_constraint(table),
                    "fks": inspector.get_foreign_keys(table),
                }
                for table in table_names
            }

        schema = await conn.run_sync(get_schema)

    print("=" * 80)
    print(f"DATABASE SCHEMA INSPECTION ({len(schema)} tables)")
    print("=" * 80)

    for table, info in schema.items():
        print(f"\n📦 Table: {table}")
        pk_cols = info["pks"].get("constrained_columns", [])
        print("  Columns:")
        for col in info["columns"]:
            name = col["name"]
            col_type = str(col["type"])
            nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
            pk = " [PRIMARY KEY]" if name in pk_cols else ""
            print(f"    • {name:28} {col_type:18} {nullable:10}{pk}")

        if info["fks"]:
            print("  Foreign Keys:")
            for fk in info["fks"]:
                referred_table = fk.get("referred_table")
                cols = ", ".join(fk.get("constrained_columns", []))
                ref_cols = ", ".join(fk.get("referred_columns", []))
                print(f"    ↳ ({cols}) -> {referred_table}({ref_cols})")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(print_schema())
