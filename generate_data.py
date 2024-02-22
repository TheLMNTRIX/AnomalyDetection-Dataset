import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Configuration 
start_date = datetime(2024, 2, 1, 7, 0, 0)  
end_date = start_date + timedelta(days=30) 
num_users = 10
num_devices = 5
num_entries = 200
main_entrance_device = "D201" 
double_entry_grace_period = timedelta(seconds=5)

# Authority Assignment
user_authorities = {f"U100{i+1}": random.randint(1, 3) for i in range(num_users)}
device_authorities = {f"D20{i+1}": random.randint(1, 3) for i in range(num_devices)}
device_authorities[main_entrance_device] = 1  

# Data generation
data = []
current_timestamp = start_date
active_entries = {} 

def attempt_to_fix_anomaly(timestamp, last_entry, grace_period):
    # Calculate time difference between entries
    time_diff = timestamp - last_entry[1]

    # Ensure adjustment exceeds both grace period and time difference
    adjusted_timestamp = timestamp + max(grace_period, time_diff + timedelta(seconds=1))
    return adjusted_timestamp, 1

for _ in range(num_entries):
    user_id = f"U100{random.randint(1, num_users)}"
    device_id = f"D20{random.randint(1, num_devices)}"
    access_type = random.choice(["Entry", "Exit"])
    user_auth = user_authorities[user_id]
    device_auth = device_authorities[device_id]
    fixed = 0 

    # Anomaly Injection (Occasional)
    anomaly_label = 0 
    if random.random() < 0.05:  
        anomaly_type = random.choice([
            ("unauthorized_access", 0.5), 
            ("after_hours", 0.3),
            ("rapid_sequence", 0.2)
        ])

        if anomaly_type[0] == "unauthorized_access":
            user_auth = random.choice([x for x in range(1,3) if x <= device_auth]) 
        elif anomaly_type[0] == "after_hours":
            timestamp = start_date + timedelta(hours=random.choice([0, 1, 2, 22, 23]))
        elif anomaly_type[0] == "rapid_sequence":
            timestamp = current_timestamp - timedelta(minutes=random.randint(1, 5))  
        anomaly_label = 1 

    # Timestamp Handling
    time_delta = timedelta(minutes=random.randint(5, 120)) 
    current_timestamp += time_delta  
    timestamp = current_timestamp
    if timestamp > end_date: 
        time_to_end = end_date - current_timestamp 
        timestamp = current_timestamp + time_to_end

    # Entry / Exit Logic 
    if access_type == "Entry":
        last_entry = active_entries.get(user_id) 
        if last_entry:
            print("Last Entry:")
            if timestamp - last_entry[1] < double_entry_grace_period:
                print("Anomaly Detected!")
                if random.random() < 0.5: 
                    print("Attempting to fix anomaly...") 
                    timestamp, fixed = attempt_to_fix_anomaly(timestamp, last_entry, double_entry_grace_period)
                    print("New Timestamp:", timestamp)
                    anomaly_label = 0  
                else:
                    fixed = 0
            else:
                fixed = 0
        else:
            fixed = 0
        active_entries[user_id] = (device_id, timestamp) 

    elif access_type == "Exit":
        if user_id not in active_entries:  
            anomaly_label = 1 
        else:
            del active_entries[user_id]  

    # Create DataFrame Row 
    data_row = [user_id, device_id, access_type, timestamp, user_auth, device_auth, anomaly_label, fixed]
    data.append(data_row) 

# Create DataFrame 
df = pd.DataFrame(data, columns=["UserID", "DeviceID", "TypeOfAccess", "TimeOfAccess", "UserAuthorityLevel", "DeviceAuthorityLevel", "Anomaly", "Fixed"])

# File Handling 
filename = "access_control_data.csv"
if not os.path.exists(filename):  
    df.to_csv(filename, index=False)  
else: 
    with open(filename, 'a') as f:  
        df.to_csv(f, index=False, header=False)  
