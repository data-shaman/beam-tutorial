import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import psycopg2
import duckdb
import logging
import sys


# Set up logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


# PostgreSQL connection details
POSTGRES_HOST = "postgres_container"
POSTGRES_PORT = "5432"
POSTGRES_DB = "website_events"
POSTGRES_USER = "postgres"
PASSWORD_PASSWORD="Passw0rd"
DUCKDB_FILE_PATH = "/data/warehouse.duckdb"

logger.info("Initiating streaming from Postgres...")

def stream_data_from_postgres():
    """
    Stream data from PostgreSQL using a server-side cursor.
    """
    connection = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=PASSWORD_PASSWORD

    )
    cursor = connection.cursor(name='streaming_cursor')  # Server-side cursor
    query= """SELECT * FROM web_events;"""
    
    try: 
        cursor.execute(query)
        logger.info("Executing SQL: {query}")
    except Exception as e:
        logger.error(f"Unnable to connect to Postgres: {e}")

    # Check if the cursor description is valid
    if cursor.description is None:
        print("No data found or query execution failed.")
        cursor.close()
        connection.close()
        return  # Exit the function early if no data is found

    columns = [desc[0] for desc in cursor.description]

    for row in cursor:
        yield dict(zip(columns, row))
    
    cursor.close()
    connection.close()


class AggregateAndNest(beam.DoFn):
    def process(self, element):  # element refers to row of data
        # Extract all fields from the element
        user_id = element['user_custom_id']
        session_id = element['user_domain_id']
        event_id = element['event_id']
        timestamp = element['event_timestamp']
        event_type = element['event_type']
        page_url = element['page_url']
        referer_url = element['referer_url']
        utm_medium = element['utm_medium']
        utm_source = element['utm_source']
        utm_content = element['utm_content']
        utm_campaign = element['utm_campaign']
        geo_latitude = element['geo_latitude']
        geo_longitude = element['geo_longitude']
        geo_country = element['geo_country']
        geo_region = element['geo_region_name']
        ip_address = element['ip_address']
        browser = element['browser_name']
        user_agent = element['browser_user_agent']
        os_name = element['os_name']
        device_type = element['device_type']
        is_mobile = element['device_is_mobile']

        # Create a nested structure for session and event data
        nested_data = {
            "user_id": user_id,
            "sessions": [{
                "session_id": session_id,
                "events": [{
                    "event_id": event_id,
                    "timestamp": timestamp,
                    "event_type": event_type,
                    "page_url": page_url,
                    "referer_url": referer_url,
                    "utm_data": {
                        "medium": utm_medium,
                        "source": utm_source,
                        "content": utm_content,
                        "campaign": utm_campaign 
                    },
                    "geo_data": {
                        "latitude": geo_latitude,
                        "longitude": geo_longitude,
                        "country": geo_country,
                        "region": geo_region
                    },
                    "ip_address": ip_address,
                    "browser_info": {
                        "name": browser,
                        "user_agent": user_agent
                    },
                    "os_name": os_name,
                    "device_info": {
                        "type": device_type,
                        "is_mobile": is_mobile
                    }
                }]
            }]
        }

        yield nested_data


def write_to_duckdb(record):
    """
    Write the aggreagated data to DuckDB.
    """
    conn = duckdb.connect(database=DUCKDB_FILE_PATH, read_only=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_aggregates (
                 user_id TEXT,
                 sessions JSON
        );
    """)
    conn.execute("""
        INSERT INTO user_aggregates (user_id, sessions)
        VALUES (?, ?);
    """, (record['user_id'], str(record['sessions'])))
    conn.close()


def run_pipeline():
    options = PipelineOptions()

    with beam.Pipeline(options=options) as p:
        # Stream data from PostgreSQL
        events = p | "Stream Data from Postgres" >> beam.Create(stream_data_from_postgres())
        
        # Perfrom aggreagtion and nesting
        nested_data = events | "Aggregate and Nest" >> beam.ParDo(AggregateAndNest())

        # Write the nested data to DuckDB
        nested_data | "Write to DuckDB" >> beam.Map(lambda record: write_to_duckdb(record))

        
if __name__ == "__main__":
    run_pipeline()
