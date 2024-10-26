import os
import re
import pandas as pd


# Define the function to clean filenames
def clean_filename(name):
    return re.sub(r'[^\w\s-]', '', name).replace(" ", "_")


# Load the CSV file
file_path = '../dataset/steam_uncleaned.csv'
steam_data = pd.read_csv(file_path)

# Define the output directory
output_dir = '../dataset/document'
os.makedirs(output_dir, exist_ok=True)

# Create a document for each game using only the title and description
for _, row in steam_data.iterrows():
    title = row['Name']
    description = row['Description']

    # Clean the filename and create a full path
    filename = f"{clean_filename(title)}.txt"
    file_path = os.path.join(output_dir, filename)

    # Write the title and description to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n{description}")

print("Documents created successfully!")
