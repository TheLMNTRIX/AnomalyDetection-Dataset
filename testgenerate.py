import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Configuration 
start_date = datetime(2024, 2, 1, 7, 0, 0)  
end_date = start_date + timedelta(days=30) 
num_users = 10
num_devices = 5
num_entries = 10000
main_entrance_device = "D201" 
double_entry_grace_period = timedelta(seconds=30)

# Authority Assignment
user_authorities = {f"U100{i+1}": random.randint(1, 3) for i in range(num_users)}
device_authorities = {f"D20{i+1}": random.randint(1, 3) for i in range(num_devices)}
device_authorities[main_entrance_device] = 1  # Ensure main entrance has authority 1
device_authorities['D206'] = 4 # High security device
active_entries = {} 

print("User Authorities:", user_authorities) 

# Initialize active_entries with entries for all users 
for user_id in user_authorities:
    user_id_for_entry = user_id[4:]  # Remove "U100" prefix
    new_key = "U100" + user_id_for_entry # Create key that matches data generation
    active_entries[new_key] = []
    user_auth = user_authorities[user_id]
    for device_id, device_auth in device_authorities.items():
        if device_auth <= user_auth:  
            timestamp = start_date - timedelta(minutes=random.randint(1, 60)) # Before start_date 
            active_entries[user_id].append((device_id, timestamp, True if device_id == main_entrance_device else False)) 



# Data generation
data = []
current_timestamp = start_date

anomaly_count = 0

for _ in range(num_entries):
    user_id = f"U100{random.randint(1, num_users)}"
    # Device Selection (Non-Anomalous)
    device_options = [d for d in device_authorities if device_authorities[d] <= user_authorities[user_id]]
    device_id = random.choice(device_options)  

    access_type = random.choice(["Entry", "Exit"])
    user_auth = user_authorities[user_id]
    device_auth = device_authorities[device_id]

    # Anomaly Injection (Occasional)
    anomaly_label = 0 
    if random.random() < 0.15:  
        anomaly_count += 1
        anomaly_type = random.choice([
            ("unauthorized_access", 0.6), 
            ("after_hours", 0.4),      
        ])

        if anomaly_type == "unauthorized_access": 
            high_security_devices = [d for d in device_authorities if device_authorities[d] == 4]  
            unauthorized_devices = [d for d in device_authorities if device_authorities[d] > user_authorities[user_id]]
            all_unauthorized = unauthorized_devices + high_security_devices # Combine the lists
            device_id = random.choice(all_unauthorized)
            anomaly_label = 1 

        elif anomaly_type == "after_hours":
            timestamp = start_date + timedelta(hours=random.choice([0, 1, 2, 22, 23]))

    # Timestamp Handling
    time_delta = timedelta(minutes=random.randint(5, 120)) 
    current_timestamp += time_delta  
    timestamp = current_timestamp

    if timestamp > end_date: 
        time_to_end = end_date - current_timestamp 
        timestamp = current_timestamp + time_to_end

   # Entry/Exit Logic 
    if access_type == "Entry":
        if user_id not in active_entries:
            active_entries[user_id] = []  
        active_entries[user_id].append((device_id, timestamp, True if device_id == main_entrance_device else False))

    elif access_type == "Exit":
        if user_id not in active_entries:  
            if random.random() < 0.4:  # 40% chance of conversion
                access_type = "Entry"  # Change to entry
                anomaly_label = 0  # No longer an anomaly
            else:
                anomaly_label = 1  
                
        else:
            # while active_entries[user_id]:  
            #     last_entry = active_entries[user_id].pop() 

            # # Existing Anomaly Checks
            #     if last_entry:  # Ensure entry exists before calculations
            #         time_inside = timestamp - last_entry[1]
            #         if time_inside > timedelta(hours=8): 
            #             anomaly_label = 1
                        

                    # if last_entry[0] != main_entrance_device and device_auth > 1:  
                    #     anomaly_label = 1 
                        

            del active_entries[user_id] 

    # Additional Office Logic 
    # last_entry = active_entries.get(user_id)
    # if last_entry:  #  Check if the stack has entries for the user
    #     if last_entry[-1]:  # Check if the latest entry actually exists 
    #         time_inside = timestamp - last_entry[-1][1]  # Access the most recent timestamp 
    #         if time_inside > timedelta(hours=8): 
    #             anomaly_label = 1
                

    #     if last_entry[-1][0] != main_entrance_device and device_auth > 1:  # Access the most recent device
    #         anomaly_label = 1 
            


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
