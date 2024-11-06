from datetime import datetime, timedelta
import json
from fake_web_events import Simulation


# Define the toal number of days and events per day
TOTAL_DAYS = 31
EVENTS_PER_DAY = 100
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

# Filename for the JSON file
file_name = "all_events.json"

# Initialse a list to collect all events
all_events = []

# print("Sample event structure:", next(simulation.run(duration_seconds=10)))

# Generate events continiously until reaching the rarget number
for event in simulation.run(duration_seconds=60 * 60 * 24 * TOTAL_DAYS):  # Run for 31 days
    # Append the event to the list
    all_events.append(event)

    # Increment the simulation time slightly (e.g., 1 second between events)
    simulation.cur_time += timedelta(seconds=1)

    # Break once the total number of events is reached
    if len(all_events) >= TOTAL_EVENTS:
        break
   
# Write all collected events to a single JSON file
with open(file_name, 'w') as f:
    json.dump(all_events, f)

print(f"Generated {TOTAL_EVENTS} events spanning 31 days, written to {file_name}")
