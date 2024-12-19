import os
import re
import pandas as pd


# Define the function to clean filenames
def clean_filename(name):
    return re.sub(r'[^\w\s-]', '', name).replace(" ", "_")


# Load the CSV file and add unique IDs
file_path = '../dataset/steam_uncleaned.csv'
# file_path = 'dataset/steam_uncleaned.csv' #Khusus untuk william fi
steam_data = pd.read_csv(file_path)
steam_data['id'] = steam_data.index + 1  # Generate unique IDs starting from 1

# Define the output directory
output_dir = '../dataset/document'
# output_dir = 'dataset/document' #Khusus untuk William FI
os.makedirs(output_dir, exist_ok=True)

# Create a document for each game with the specified structure
for _, row in steam_data.iterrows():
    title = row['Name']
    price = row['Price'] if 'Price' in row else "N/A"
    release_date = row['Release_date'] if 'Release_date' in row else "N/A"
    review_no = row['Review_no'] if 'Review_no' in row else "N/A"
    review_type = row['Review_type'] if 'Review_type' in row else "N/A"
    tags = row['Tags'] if 'Tags' in row else "N/A"
    description = row['Description']

    doc_id = row['id']

    # Clean the filename and create a full path
    filename = f"{doc_id}_{clean_filename(title)}.txt"
    file_path = os.path.join(output_dir, filename)

    # Write the details to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"Name: {title}\n")
        f.write(f"Price: {price}\n")
        f.write(f"Release_date: {release_date}\n")
        f.write(f"Review_no: {review_no}\n")
        f.write(f"Review_type: {review_type}\n")
        f.write(f"Tags: {tags}\n")
        f.write(f"Description: {description}\n")

print("Documents created successfully!")
