import re
import pandas as pd

def parse_subject_mappings(js_file_path):
    with open(js_file_path, 'r', encoding='utf-8') as file:
        js_content = file.read()

    subjects = []
    pattern = re.compile(r'ds_subject\[ds_subject\.length\]\s*=\s*{([^}]+)}')
    matches = pattern.findall(js_content)

    for match in matches:
        subject = {}
        items = re.findall(r'(\w+):\s*([^,}]+)', match)
        for key, value in items:
            key = key.strip()
            value = value.strip().strip('"\'')
            subject[key] = value
        subjects.append(subject)

    return subjects

# Path to your subjects.js file
js_file_path = '4_subjectId_subjectName_mapping.js'

# Parse subject mappings
subject_mappings = parse_subject_mappings(js_file_path)

# Create a DataFrame from the subject mappings
df = pd.DataFrame(subject_mappings)

# Save the DataFrame to an Excel file
df.to_excel('4_subject_mappings.xlsx', index=False)

print("Subject mappings have been saved to 'subject_mappings.xlsx'")