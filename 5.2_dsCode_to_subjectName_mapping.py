# ds_subjectId_mapping.js se Dscode is being mapped to subjectID. We import the excel file subject_mappings
# which has mapping of subjectID with subjectName. Now using the two, DScode is mapped to subjectName
 
import re
import pandas as pd

def parse_ds_array(js_file_path):
    with open(js_file_path, 'r', encoding='utf-8') as file:
        js_content = file.read()

    pattern = re.compile(r'ds_array\[\d+\]\s*=\s*{([^}]+)}')
    entries = pattern.findall(js_content)

    ds_data = []
    for entry in entries:
        ds_entry = {}
        # Use regex to split the entry, preserving quoted values
        items = re.findall(r'(\w+):\s*("[^"]*"|[^,]+)(?:,|$)', entry)
        for key, value in items:
            value = value.strip().strip('"')
            ds_entry[key] = value
        
        # Split subjects
        subjects = ds_entry.get('subject', '').split('#')
        ds_entry['subjects'] = subjects
        
        ds_data.append(ds_entry)

    return ds_data

# Path to your data.js file
js_file_path = '5_ds_subjectId_mapping.js'

# Parse DS array
ds_data = parse_ds_array(js_file_path)

# Create a DataFrame from the parsed data
df = pd.DataFrame(ds_data)

# Read the subject mappings Excel file
subject_df = pd.read_excel('4_subject_mappings.xlsx')

# Create a dictionary for quick subject name lookup
subject_dict = dict(zip(subject_df['subject_id'], subject_df['subject_name']))

# Function to get subject name
def get_subject_name(subject_id):
    return subject_dict.get(subject_id, 'Unknown')

# Create separate columns for each subject (up to 5 subjects)
for i in range(5):
    df[f'Subject_{i+1}_Code'] = df['subjects'].apply(lambda x: x[i] if i < len(x) else None)
    df[f'Subject_{i+1}_Name'] = df[f'Subject_{i+1}_Code'].apply(get_subject_name)

# Select and rename the columns we want
columns_to_keep = ['code', 'title', 'origin', 'destination', 'start_date', 
                   'Subject_1_Code', 'Subject_1_Name', 
                   'Subject_2_Code', 'Subject_2_Name', 
                   'Subject_3_Code', 'Subject_3_Name', 
                   'Subject_4_Code', 'Subject_4_Name', 
                   'Subject_5_Code', 'Subject_5_Name']

final_df = df[columns_to_keep]

# Rename columns
final_df = final_df.rename(columns={
    'code': 'DS Code',
    'title': 'Title',
    'origin': 'Origin',
    'destination': 'Destination',
    'start_date': 'Start Date'
})

# Function to convert DS Code to integer
def ds_code_to_int(ds_code):
    return int(ds_code.replace('DS', ''))

# Convert DS Code to integer
final_df['DS Code'] = final_df['DS Code'].apply(ds_code_to_int)

# Sort the dataframe by DS Code (now an integer)
final_df = final_df.sort_values('DS Code')

# Save the final dataframe to a new Excel file
final_df.to_excel('5_ds_code_subject_mapping.xlsx', index=False)

print("DS code and subject mapping has been saved to 'ds_code_subject_mapping.xlsx'")

# Print some statistics
print(f"Total number of entries: {len(final_df)}")
print(f"Number of unique DS Codes: {final_df['DS Code'].nunique()}")
print(f"Number of DS codes with multiple subjects: {(final_df['Subject_2_Code'].notna().sum())}")