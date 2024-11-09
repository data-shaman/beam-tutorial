import os
import fastavro
import psycopg2
from psycopg2 import sql
from fake_web_events import Simulation


# PostgreSQL database connection details
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = "5432"
DB_NAME = os.environ.get('POSTGRES_DB')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

# Define Avro schema
avro_schema = {
    "type": "record",
    "name": "WebEvent",
    "fields": [
        {"name":"event_id", "type": "string"},
        {"name":"event_timestamp", "type": "string"},
        {"name":"event_type", "type": "string"},
        {"name":"page_url", "type": "string"},
        {"name":"page_url_path", "type": "string"},
        {"name":"referer_url", "type": "string"},
        {"name":"referer_url_scheme", "type": "string"},
        {"name":"referer_url_port", "type": "string"},
        {"name":"referer_medium", "type": "string"},
        {"name":"utm_medium", "type": "string"},
        {"name":"utm_source", "type": "string"},
        {"name":"utm_content", "type": "string"},
        {"name":"utm_campaign", "type": "string"},
        {"name":"click_id", "type": ["null", "string"]},
        {"name":"geo_latitude", "type": ["null", "string"]},
        {"name":"geo_longitude", "type": ["null", "string"]},
        {"name":"geo_country", "type": "string"},
        {"name":"geo_timezone", "type": "string"},
        {"name":"geo_region_name", "type": "string"},
        {"name":"ip_address", "type": "string"},
        {"name":"browser_name", "type": "string"},
        {"name":"browser_user_agent", "type": "string"},
        {"name":"browser_language", "type": "string"},
        {"name":"os", "type": "string"},
        {"name":"os_name", "type": "string"},
        {"name":"os_timezone", "type": "string"},
        {"name":"device_type", "type": "string"},
        {"name":"device_is_mobile", "type": ["null", "string", "boolean"]},
        {"name":"user_custom_id", "type": "string"},
        {"name":"user_domain_id", "type": ["null", "string"]}
    ]
}

# Initialise the simulation
simulation = Simulation(user_pool_size=1000, sessions_per_day=100)

# Write to Avro file
print("Writing events to Avro...")
with open("web_events.avro", "wb") as out_file:
    writer = fastavro.writer(out_file, avro_schema, simulation.run(duration_seconds=60))

print("Avro file created")

# Connect to the PostgreSQL database
connection = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD

)
cursor = connection.cursor()

print("Connection sucessful!")

# Helper function to map Avro types to Postgres types
def map_avro_to_postgres(avro_type):
    type_mapping = {
        "string": "TEXT",
        "float": "REAL",
        "timestamp-millis": "TIMESTAMP"
    }
    if isinstance(avro_type, list):
        # Handle union types (e.g. ["nulll", "string"])
        avro_type = [t for t in avro_type if t != "null"][0]
    return type_mapping.get(avro_type, "TEXT")

# Create table based on Avro schema
table_name = "web_events"
fields = avro_schema["fields"]
columns = []

for field in fields:
    column_name = field["name"]
    avro_type = field["type"]
    postgres_type = map_avro_to_postgres(avro_type)
    columns.append(f"{column_name} {postgres_type}")

create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"

cursor.execute(create_table_query)
connection.commit()

print(f"Table '{table_name}' created successfully!")

# Insert data into PostgreSQL
with open("web_events.avro", "rb") as avro_file:
    reader = fastavro.reader(avro_file)
    for record in reader:
        columns = list(record.keys())
        values = list(record.values())

        # Replace None values with NULL and convert to appropriate types
        values = [value if value is not None else None for value in values]

        insert_query = sql.SQL("INSERT into {table} ({fields}) VALUES ({placeholders})").format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(', ').join(sql.Placeholder() * len(values))
        )
        cursor.execute(insert_query, values)

# Commit the transaction and close the connection
connection.commit()
cursor.close()
connection.close()

print("Data inserted into the PostgreSQL 'web_events' table")
