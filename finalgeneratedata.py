import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Configuration 
start_date = datetime(2024, 2, 1, 7, 0, 0)  
end_date = start_date + timedelta(days=30) 
num_users = 10
num_devices = 5
num_entries = 100
main_entrance_device = "D201" 

# Authority Assignment
user_authorities = {f"U100{i+1}": random.randint(1, 3) for i in range(num_users)}
device_authorities = {f"D20{i+1}": random.randint(1, 3) for i in range(num_devices)}
device_authorities[main_entrance_device] = 1  # Ensure main entrance has authority 1

# Data generation
data = []
current_timestamp = start_date
active_entries = {} 
anomaly_count = 0
for _ in range(num_entries):
    user_id = f"U100{random.randint(1, num_users)}"
    device_id = f"D20{random.randint(1, num_devices)}"
    access_type = random.choice(["Entry", "Exit"])
    user_auth = user_authorities[user_id]
    device_auth = device_authorities[device_id]

    # Anomaly Injection (Occasional)
    anomaly_label = 0 
    if random.random() < 0.05:  
        anomaly_count += 1
        anomaly_type = random.choice([
            "unauthorized_access", 
            "after_hours",
            "rapid_sequence"
        ])

        if anomaly_type == "unauthorized_access":
            #print("Device Authority:", device_auth) 
            user_auth = random.choice([x for x in range(1, 3) if x <= device_auth]) 
        elif anomaly_type == "after_hours":
            timestamp = start_date + timedelta(hours=random.choice([0, 1, 2, 22, 23]))
        elif anomaly_type == "rapid_sequence":
            timestamp = current_timestamp - timedelta(minutes=random.randint(1, 5))  
        anomaly_label = 1 

    # Timestamp Handling
    time_delta = timedelta(minutes=random.randint(5, 120)) 
    current_timestamp += time_delta  
    timestamp = current_timestamp

    if timestamp > end_date: 
        time_to_end = end_date - current_timestamp 
        timestamp = current_timestamp + time_to_end

    # Entry/Exit Logic 
    if access_type == "Entry":
        if user_id in active_entries:  
            if active_entries[user_id][0] == device_id: 
                anomaly_label = 1  
        active_entries[user_id] = (device_id, timestamp) 
    elif access_type == "Exit":
        if user_id in active_entries:
            del active_entries[user_id]  
        else: 
            anomaly_label = 1 

    # Additional Office Logic 
    last_entry = active_entries.get(user_id)
    if last_entry:
        time_inside =  timestamp - last_entry[1]
        if time_inside > timedelta(hours=8): 
            anomaly_label = 1

        if last_entry[0] != main_entrance_device and device_auth > 1: 
            anomaly_label = 1  

    # Create DataFrame Row 
    data_row = [user_id, device_id, access_type, timestamp, user_auth, device_auth, anomaly_label] 
    data.append(data_row)

print("Total Entries:", num_entries)
print("Entries with Anomalies:", anomaly_count) 

# Create DataFrame 
df = pd.DataFrame(data, columns=["UserID", "DeviceID", "TypeOfAccess", "TimeOfAccess", "UserAuthorityLevel", "DeviceAuthorityLevel", "Anomaly"])

# File Handling 
filename = "access_control_data.csv"
if not os.path.exists(filename):  
    df.to_csv(filename, index=False)  
else: 
    with open(filename, 'a') as f:  
        df.to_csv(f, index=False, header=False)  
