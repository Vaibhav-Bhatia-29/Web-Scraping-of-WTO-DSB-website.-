import os
import re
from bs4 import BeautifulSoup
import pandas as pd

def extract_js_object(text):
    obj = {}
    for line in text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().strip('"')
            value = value.strip().strip(',').strip('"')
            obj[key] = value
    return obj

# Load the agreement and article data
with open('3.1_articles_agreements.js', 'r') as f:
    js_content = f.read()

# Extract agreement data
agreement_data = re.findall(r'ds_agreement\[\d+\]\s*=\s*({[^}]+})', js_content)
agreements = {}

for data in agreement_data:
    agreement = extract_js_object(data)
    if 'agreement_short_name' in agreement and 'agreement_url' in agreement:
        agreements[agreement['agreement_url']] = agreement['agreement_short_name']
        
        # Add sub-agreements if they exist
        if 'agreement_sub_page' in agreement and agreement['agreement_sub_page']:
            sub_pages = agreement['agreement_sub_page'].split('#')
            for sub_page in sub_pages:
                sub_url = sub_page.split('*')[0]
                agreements[sub_url] = agreement['agreement_short_name']

# Extract article data
article_data = re.findall(r'ds_article\[ds_article\.length\]\s*=\s*({[^}]+})', js_content)
articles = {}
for data in article_data:
    article = extract_js_object(data)
    if 'article_bookmark' in article and 'article_name' in article:
        articles[article['article_bookmark']] = article['article_name']

# Load existing Excel file
df = pd.read_excel('wto_dispute_cases.xlsx')

# Directory containing the HTML files
directory = "wto_cases_data"

def extract_agreements(soup, agreements, articles):
    agreement_articles = {}
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if href.startswith('/english/docs_e/legal_e/'):
            parts = href.split('/')[-1].split('#')
            agreement_url = parts[0]
            article_bookmark = parts[1] if len(parts) > 1 else ''
            
            agreement_name = agreements.get(agreement_url, agreement_url)
            article_name = articles.get(article_bookmark, article_bookmark)
            
            if agreement_name not in agreement_articles:
                agreement_articles[agreement_name] = set()
            agreement_articles[agreement_name].add(article_name)
    
    if not agreement_articles:
        return 'N/A'
    
    result = []
    for agreement, arts in agreement_articles.items():
        articles_str = ', '.join(sorted(arts))
        result.append(f"{agreement}: {articles_str}")
    
    return '; '.join(result)

# Iterate over the files in the "wto_cases_data" directory
for file in os.listdir(directory):
    if file.endswith(".html"):
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # Extract Case No by removing the .html extension and converting to int
            case_no = int(file.split('ds')[1].replace('.html', ''))
            
            # Extract Agreements cited
            agreements_cited = extract_agreements(soup, agreements, articles)
            
            # Update the DataFrame
            df.loc[df['Case No.'] == case_no, 'Agreements Cited'] = agreements_cited

# Save the updated DataFrame to the Excel file
df.to_excel('wto_dispute_cases.xlsx', index=False)

print("Data extraction and saving to Excel completed.")
