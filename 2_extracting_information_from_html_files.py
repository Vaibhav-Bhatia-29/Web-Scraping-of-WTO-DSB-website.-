import os
import re
from bs4 import BeautifulSoup
import pandas as pd

# Create a list to store all case data
all_cases = []

# Directory containing the HTML files
directory = "wto_cases_data"

# Iterate over the files in the "wto_cases_data" directory
for file in os.listdir(directory):
    if file.endswith(".html"):
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # Extract Case No by removing the .html extension and converting to int
            case_no = int(file.split('ds')[1].replace('.html', ''))
            
            # Find the key facts table
            key_facts_table = soup.find('table', {'id': 'keyFactsTbl'})
            
            if key_facts_table:
                # Extract Complainant
                complainant_row = key_facts_table.find('td', string='Complainant: ')
                complainant = complainant_row.find_next_sibling('td').text.strip() if complainant_row else 'N/A'
                
                # Extract Respondent
                respondent_row = key_facts_table.find('td', string='Respondent:')
                respondent = respondent_row.find_next_sibling('td').text.strip() if respondent_row else 'N/A'
                
                # Extract Date of Consultation
                consultation_row = key_facts_table.find('td', string=lambda text: text and 'Consultations requested' in text)
                if not consultation_row:
                    consultation_row = key_facts_table.find('a', string=lambda text: text and 'Consultations requested' in text)
                    if consultation_row:
                        consultation_row = consultation_row.find_parent('td')
                consultation_date = consultation_row.find_next_sibling('td').text.strip() if consultation_row else 'N/A'
            else:
                complainant = respondent = consultation_date = 'N/A'

            # Extract Agreements cited
            agreements_cited = []
            links = soup.find_all('a', href=True)
            pattern = re.compile(r'art(\d+)')
            for link in links:
                href = link['href']
                match = pattern.search(href)
                if match:
                    agreements_cited.append(match.group(1))

            agreements_cited = '; '.join(set(agreements_cited)) if agreements_cited else 'N/A'
            
            # Extract Summary (all paragraphs after "Consultations" and before "Withdrawal/termination")
            consultations_heading = soup.find('h3', string='Consultations')
            summary = ''
            if consultations_heading:
                summary_siblings = consultations_heading.find_next_siblings()
                for sibling in summary_siblings:
                    if sibling.name == 'h3' and 'Withdrawal/termination' in sibling.text:
                        break
                    if sibling.name == 'p':
                        summary += sibling.text.strip() + ' '
            
                # Extract One-page summary link
                summary_link = soup.find('a', string='One-page summary of key  findings of this dispute')
                if summary_link:
                    relative_path = summary_link['href']
                    one_page_summary_link = f"https://www.wto.org{relative_path}"
                else:
                    one_page_summary_link = 'N/A'
                
          
            # Append the data to the list
            all_cases.append({
                'Case No.': case_no,
                'Complainant': complainant,
                'Respondent': respondent,
                'Date of Consultation': consultation_date,
                'Agreements Cited': agreements_cited,
                'Summary': summary.strip(),
                'One-page Summary Link': one_page_summary_link
            })

# Create a DataFrame from the list of cases
df = pd.DataFrame(all_cases)

# Save the DataFrame to an Excel file
df.to_excel('wto_dispute_cases.xlsx', index=False)

print("Data extraction and saving to Excel completed.")