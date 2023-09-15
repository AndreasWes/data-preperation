import os
import pandas as pd
import numpy as np

file_path = "C:\Users\user\Documents\Rally\Telemetry\data preperation\data_path.txt"
data_dir = ""

with open(file_path, "r") as file:
    for line in file:
        if "data_dir" in line:
            data_dir = line.split("=")[1].strip()
            break

print(data_dir)

# List of CSV files
csv_files = [
    'Accelerometer.csv',
    'Gyroscope.csv',
    'Location.csv',
    'Magnetometer.csv'
]

# Target path for the combined and resampled data
combined_output_path = r'C:\Users\user\Documents\Rally\Telemetry\data preperation\combined_data.csv'
# Target path for the combined and resampled data
prepared_output_path = r'C:\Users\user\Documents\Rally\Telemetry\data preperation\prepared_data.csv'

# Sampling rate for resampling
target_sampling_rate = 10  # 10 Hz

# Initialize an empty list to store DataFrames
dfs = []

# Iterate over the CSV files and process them
for csv_file in csv_files:
    input_path = os.path.join(data_dir, csv_file)
    
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(input_path)
    
    # Set the time as the index (assuming "Time (s)" is the time column)
    df['Time (s)'] = pd.to_datetime(df['Time (s)'], unit='s')
    df.set_index('Time (s)', inplace=True)
    
    # Resample and linearly interpolate
    df_resampled = df.resample(f'{1/target_sampling_rate}S').mean().interpolate(method='linear')
    
    # Append the resampled DataFrame to the list
    dfs.append(df_resampled)

# Combine the resampled DataFrames into one DataFrame
combined_df = pd.concat(dfs, axis=1)
# Remove rows with NaN values from the DataFrame
combined_df = combined_df.dropna()

# Save the combined DataFrame to a CSV file
combined_df.to_csv(combined_output_path)

#############################################################################

combined_df_inter=combined_df
# Berechnen Sie die Mittelwerte der Beschleunigungsspalten
combined_df_inter['Acceleration x (m/s^2)'] = combined_df['Acceleration x (m/s^2)'] - combined_df['Acceleration x (m/s^2)'].mean()
combined_df_inter['Acceleration y (m/s^2)'] = combined_df['Acceleration y (m/s^2)'] - combined_df['Acceleration y (m/s^2)'].mean()
combined_df_inter['Acceleration z (m/s^2)'] = combined_df['Acceleration z (m/s^2)'] - combined_df['Acceleration z (m/s^2)'].mean()

# Berechnen Sie die Spalte atan(Magnetic field y / Magnetic field z)
# Define the conversion function
def convert_to_positive_azimuth(azimuth_degrees):
    if azimuth_degrees < 0:
        azimuth_degrees += 360.0
    elif azimuth_degrees > 360.0:
        azimuth_degrees -= 360.0
    return azimuth_degrees


combined_df_inter["B"] = np.sqrt(combined_df["Magnetic field x (µT)"]**2 + combined_df["Magnetic field y (µT)"]**2 + combined_df["Magnetic field z (µT)"]**2)
combined_df_inter["Magnetic_Field_x_normalized"] = combined_df["Magnetic field x (µT)"] / combined_df_inter["B"]
combined_df_inter["Magnetic_Field_y_normalized"] = combined_df["Magnetic field y (µT)"] / combined_df_inter["B"]
combined_df_inter["Magnetic_Field_z_normalized"] = combined_df["Magnetic field z (µT)"] / combined_df_inter["B"]
combined_df_inter["inclination"] = np.arctan2(combined_df_inter["Magnetic_Field_z_normalized"], np.sqrt(combined_df_inter["Magnetic_Field_x_normalized"]**2 + combined_df_inter["Magnetic_Field_y_normalized"]**2))
combined_df_inter["azimuth"] = np.arctan2(combined_df_inter["Magnetic_Field_y_normalized"], combined_df_inter["Magnetic_Field_x_normalized"])
combined_df_inter["inclination_degrees"] = combined_df_inter["inclination"] * (180.0 / np.pi)
combined_df_inter["azimuth_degrees"] = combined_df_inter["azimuth"] * (360.0 / np.pi)+90
# Apply the conversion function to the 'azimuth' column
combined_df_inter['Mag Direction (°)'] = combined_df_inter["azimuth_degrees"].apply(convert_to_positive_azimuth)
# Die gewünschten Spalten auswählen
prepared_df = combined_df_inter[[ 
                      'Acceleration x (m/s^2)', 
                      'Acceleration y (m/s^2)', 
                      'Acceleration z (m/s^2)', 
                      'Gyroscope x (rad/s)', 
                      'Gyroscope y (rad/s)', 
                      'Gyroscope z (rad/s)', 
                      'Latitude (°)', 
                      'Longitude (°)', 
                      'Height (m)', 
                      'Velocity (m/s)', 
                      'Direction (°)', 
                      'Mag Direction (°)']]

# Umbenennen der Spalten
prepared_df.columns = [ 
                      'Acceleration x (m/s^2)', 
                      'Acceleration y (m/s^2)', 
                      'Acceleration z (m/s^2)', 
                      'Gyroscope x (rad/s)', 
                      'Gyroscope y (rad/s)', 
                      'Gyroscope z (rad/s)', 
                      'Latitude (°)', 
                      'Longitude (°)', 
                      'Height (m)', 
                      'Velocity (m/s)', 
                      'Direction (°)', 
                      'Mag Direction (°)']


# Save the combined DataFrame to a CSV file
prepared_df.to_csv(prepared_output_path)

print("Resampling and combining completed.")
