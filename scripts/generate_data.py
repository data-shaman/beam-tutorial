import os
import psycopg2
from datetime import datetime, timedelta
import json
from fake_web_events import Simulation


# Define the toal number of days and events per day
TOTAL_DAYS = 31
EVENTS_PER_DAY = 1000
TOTAL_EVENTS = TOTAL_DAYS * EVENTS_PER_DAY

# Set the starting date (adjust is you want a different start date)
start_date = datetime.now() - timedelta(days=TOTAL_DAYS)

# Initialise the simulation
simulation = Simulation(
    user_pool_size=int(TOTAL_EVENTS // 10),
    sessions_per_day=int(TOTAL_EVENTS)
    )

# Set the simulation's current time to start from `start_date`
simulation.cur_time = start_date

# PostgreSQL database connection details
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = "5432"
DB_NAME = os.environ.get('POSTGRES_DB')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD') 

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

# Create events table
query = """
CREATE TABLE events (
    event_id TEXT,
    event_timestamp TIMESTAMP,
    event_type TEXT,
    page_url TEXT,
    page_url_path TEXT,
    referer_url TEXT,
    referer_url_scheme TEXT,
    referer_url_port TEXT,
    referer_medium TEXT,
    utm_medium TEXT,
    utm_source TEXT,
    utm_content TEXT,
    utm_campaign TEXT,
    click_id UUID,
    geo_latitude FLOAT,
    geo_longitude FLOAT,
    geo_country TEXT,
    geo_timezone TEXT,
    geo_region_name TEXT,
    ip_address INET,
    browser_name TEXT,
    browser_user_agent TEXT,
    browser_language TEXT,
    os TEXT,
    os_name TEXT,
    os_timezone TEXT,
    device_type TEXT,
    device_is_mobile BOOLEAN,
    user_custom_id TEXT,
    user_domain_id UUID
);
"""
cursor.execute(query)

event_count = 0

column_names = [
    "event_id",
    "event_timestamp",
    "event_type",
    "page_url",
    "page_url_path",
    "referer_url",
    "referer_url_scheme",
    "referer_url_port",
    "referer_medium",
    "utm_medium",
    "utm_source",
    "utm_content",
    "utm_campaign",
    "click_id",
    "geo_latitude",
    "geo_longitude",
    "geo_country",
    "geo_timezone",
    "geo_region_name",
    "ip_address",
    "browser_name",
    "browser_user_agent",
    "browser_language",
    "os",
    "os_name",
    "os_timezone",
    "device_type",
    "device_is_mobile",
    "user_custom_id",
    "user_domain_id"
    ]

columns_str = ", ".join(column_names)

# Generate events continuously and insert them into the database 
for event in simulation.run(duration_seconds=60 * 60 * 24 * TOTAL_DAYS):  # Run for 31 days
    # Increment the simulation time slightly (1 second between events)
    simulation.cur_time += timedelta(seconds=1)

    # Extract values based on the dynamically determined columns
    values = tuple(event[col] for col in column_names)

    # Insert the event into the PostgreSQL table
    try:
        insert_query = f"INSERT INTO events ({columns_str}) VALUES ({values})"
        cursor.execute(insert_query, values)
    except Exception as e:
        print(f'Insertion failed: {e}')
    event_count += 1
    
    # Break once the total number of events is reached
    if event_count >= TOTAL_EVENTS:
        break

# Commit the transaction and close the connection
connection.commit()
cursor.close()
connection.close()

print(f"Inserted {event_count} events into the PostgreSQL 'events' table")
