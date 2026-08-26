#!/usr/bin/env python3
"""
Automated PubMed scraper for Brandon Westover's publications.

This script:
1. Searches PubMed for papers by "Westover MB" 
2. Automatically categorizes them based on keywords
3. Updates the existing YAML publication files
4. Can be run periodically to keep publications up to date
"""

import json
import os
import re
import time
import yaml
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import xml.etree.ElementTree as ET


CDAC_DOWNLOADS_API = "https://api.github.com/repos/bdsp-core/cdac-downloads/contents/"
CDAC_DOWNLOADS_BASE = "https://bdsp-core.github.io/cdac-downloads/"
PDF_PMID_RE = re.compile(r"_(\d{7,9})\.pdf$", re.IGNORECASE)

# PMIDs that PubMed's "Westover MB[Author]" search returns but do not actually
# belong to Brandon Westover (different M. Westover, ambiguous author records,
# etc.). Confirmed with the PI; never add these to the publication YAMLs.
EXCLUDE_PMIDS = {
    "37245479",  # Einizade et al, ProductGraphSleepNet (no Westover author)
    "36131149",  # Huang et al, AI foundation for therapeutic science (no Westover)
    "34889311",  # Kanth et al, Cancer Risk in Serrated Polyposis (different M Westover)
}


def fetch_pdf_pmid_map():
    """Return {PMID: download_url} for PDFs in the cdac-downloads repo whose
    filename ends with _<PMID>.pdf. Falls back to {} on any network error."""
    try:
        req = Request(CDAC_DOWNLOADS_API, headers={"Accept": "application/vnd.github+json"})
        with urlopen(req, timeout=30) as resp:
            items = json.loads(resp.read())
    except Exception as e:
        print(f"WARN: could not fetch cdac-downloads listing ({e}); new entries will link to PubMed only.")
        return {}
    out = {}
    for it in items:
        if it.get("type") != "file":
            continue
        name = it.get("name", "")
        m = PDF_PMID_RE.search(name)
        if m:
            out[m.group(1)] = CDAC_DOWNLOADS_BASE + name
    print(f"Loaded PMID→PDF map with {len(out)} entries from cdac-downloads")
    return out


class PubMedScraper:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.email = "westover@mgh.harvard.edu"  # Required for API usage
        self.pdf_pmid_map = fetch_pdf_pmid_map()
        
        # Define category mappings based on keywords
        self.category_keywords = {
            'yamlICUEEGterminology': ['icu eeg', 'critical care eeg', 'terminology', 'nomenclature'],
            'yamlQEEG': ['quantitative eeg', 'qeeg', 'spectrogram', 'spectral', 'power spectral'],
            'yamlcEEG': ['continuous eeg', 'ceeg', 'monitoring'],
            'yamlszRisk': ['seizure risk', 'seizure prediction', 'risk assessment'],
            'yamlseizures': ['seizure', 'seizures', 'epileptic', 'ictal'],
            'yamlstatusEpilepticus': ['status epilepticus', 'refractory status'],
            'yamlszIIIC': ['ictal-interictal', 'iiic', 'periodic discharge', 'rhythmic pattern'],
            'yamlszIIIC_harm': ['seizure outcome', 'iiic outcome', 'harm'],
            'yamltpw': ['triphasic wave', 'triphasic'],
            'yamlSAH': ['subarachnoid hemorrhage', 'sah', 'aneurysm'],
            'yamlPTE': ['post-traumatic epilepsy', 'pte', 'traumatic brain injury'],
            'yamldelirium': ['delirium', 'encephalopathy', 'altered mental status'],
            'yamlcarT': ['car-t', 'car t cell', 'chimeric antigen receptor', 'icans'],
            'yamlcardiacArrest': ['cardiac arrest', 'coma', 'anoxic brain injury', 'post-cardiac arrest'],
            'yamlburstSuppression': ['burst suppression', 'burst-suppression'],
            'yamlclosedLoopControl': ['closed loop', 'neurofeedback', 'brain-computer interface'],
            'yamlsleepStaging': ['sleep staging', 'sleep stages', 'rem sleep', 'nrem sleep'],
            'yamlbreathing': ['breathing', 'respiratory', 'apnea', 'ventilation'],
            'yamlinsomnia': ['insomnia', 'sleep disorder'],
            'yamlbrainAge': ['brain age', 'bai', 'aging'],
            'yamlspindles': ['sleep spindle', 'spindles', 'sigma activity'],
            'yamldementia': ['dementia', 'alzheimer', 'cognitive decline'],
            'yamlspikeDetection': ['spike detection', 'epileptiform discharge', 'ied'],
            'yamlnoiseAndBias': ['noise', 'bias', 'artifact'],
            'yamlszForecasting': ['seizure forecast', 'seizure anticipation'],
            'yamlepilepsySurgery': ['epilepsy surgery', 'surgical outcome'],
            'yamleeg': ['electroencephalography', 'eeg'],
            'yamlconnectivity': ['connectivity', 'network', 'brain network'],
            'yamlcompNeuro': ['computational neuroscience', 'neural model', 'simulation'],
            'yamldecisionAnalysis': ['decision analysis', 'decision making'],
            'yamlnon_neuro_informatics': ['health informatics', 'medical informatics'],
            'yamlML_AI': ['machine learning', 'artificial intelligence', 'deep learning', 'neural network'],
            'yamlriskPrediction': ['risk prediction', 'predictive model'],
            'yamlehrPhenotyping': ['electronic health record', 'ehr', 'phenotyping', 'nlp', 'natural language'],
            'yamltimeSeries': ['time series', 'signal processing'],
            'yamlcovid': ['covid', 'sars-cov-2', 'coronavirus'],
            'yamlprobStatsCausal': ['statistics', 'probability', 'causal inference', 'bayesian'],
            'yamlinfoTheory': ['information theory', 'entropy', 'mutual information'],
            'yamlsedationAndAnesthesia': ['sedation', 'anesthesia', 'anesthetic'],
            'yamlgenNeuro': ['neurology', 'neurological'],
            'yamlHRV_ECG': ['heart rate variability', 'hrv', 'ecg', 'electrocardiogram']
        }

    def search_pubmed(self, query, max_results=1000):
        """Search PubMed for publications."""
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'email': self.email,
            'tool': 'publication_scraper'
        }
        
        search_url = self.base_url + 'esearch.fcgi?' + urlencode(search_params)
        
        try:
            response = urlopen(search_url)
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Extract PMIDs
            pmids = []
            for id_elem in root.findall('.//Id'):
                pmids.append(id_elem.text)
            
            print(f"Found {len(pmids)} publications for query: {query}")
            return pmids
            
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []

    def fetch_publication_details(self, pmids):
        """Fetch detailed information for publications."""
        if not pmids:
            return []
            
        # Split into batches of 200 (API limit)
        batch_size = 200
        all_publications = []
        
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i + batch_size]
            pmid_string = ','.join(batch_pmids)
            
            fetch_params = {
                'db': 'pubmed',
                'id': pmid_string,
                'retmode': 'xml',
                'email': self.email,
                'tool': 'publication_scraper'
            }
            
            fetch_url = self.base_url + 'efetch.fcgi?' + urlencode(fetch_params)
            
            try:
                response = urlopen(fetch_url)
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                # Parse publications
                for article in root.findall('.//PubmedArticle'):
                    pub = self.parse_article(article)
                    if pub and pub.get('pmid') not in EXCLUDE_PMIDS:
                        all_publications.append(pub)
                        
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching publication details: {e}")
                continue
                
        return all_publications

    def parse_article(self, article):
        """Parse a single article from PubMed XML."""
        try:
            # Basic article info
            medline_citation = article.find('.//MedlineCitation')
            pmid = medline_citation.find('.//PMID').text
            
            # Title
            title_elem = medline_citation.find('.//ArticleTitle')
            if title_elem is not None and title_elem.text:
                title = title_elem.text.strip()
            else:
                title = "Unknown Title"
            
            # Authors
            authors = []
            author_list = medline_citation.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name = author.find('.//LastName')
                    initials = author.find('.//Initials')
                    if last_name is not None and initials is not None:
                        authors.append(f"{last_name.text} {initials.text}")
            
            authors_str = ', '.join(authors)
            
            # Journal info
            journal_elem = medline_citation.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else ""
            
            # Publication date
            pub_date = medline_citation.find('.//PubDate')
            year = ""
            if pub_date is not None:
                year_elem = pub_date.find('.//Year')
                year = year_elem.text if year_elem is not None else ""
            
            # Volume, Issue, Pages
            volume_elem = medline_citation.find('.//Volume')
            volume = volume_elem.text if volume_elem is not None else ""
            
            issue_elem = medline_citation.find('.//Issue')
            issue = issue_elem.text if issue_elem is not None else ""
            
            pages_elem = medline_citation.find('.//MedlinePgn')
            pages = pages_elem.text if pages_elem is not None else ""
            
            # DOI
            doi = ""
            for elocation in medline_citation.findall('.//ELocationID'):
                if elocation.get('EIdType') == 'doi':
                    doi = elocation.text
                    break
            
            # Abstract (for categorization)
            abstract_elem = medline_citation.find('.//Abstract/AbstractText')
            if abstract_elem is not None and abstract_elem.text:
                abstract = abstract_elem.text.strip()
            else:
                abstract = ""
            
            # Build display string
            display_parts = []
            if journal:
                display_parts.append(journal)
            if year:
                display_parts.append(year)
            if volume:
                vol_str = f"{volume}"
                if issue:
                    vol_str += f"({issue})"
                display_parts.append(vol_str)
            if pages:
                display_parts.append(pages)
            if doi:
                display_parts.append(f"doi: {doi}")
            display_parts.append(f"PMID: {pmid}")
            
            display = '. '.join(display_parts) + '.'
            
            # Prefer a local PDF in the cdac-downloads repo (_PMID.pdf naming)
            # over the bare PubMed URL when one is available.
            link_url = self.pdf_pmid_map.get(pmid) or f'https://pubmed.ncbi.nlm.nih.gov/{pmid}'

            # Build publication object
            publication = {
                'title': f'"{title}"',
                'image': '',
                'description': '',
                'authors': authors_str,
                'link': {
                    'url': link_url,
                    'display': display
                },
                'highlight': 0,
                'pmid': pmid,
                'abstract': abstract,
                'year': int(year) if year.isdigit() else 0
            }
            
            return publication
            
        except Exception as e:
            print(f"Error parsing article: {e}")
            return None

    def categorize_publication(self, publication):
        """Categorize a publication based on keywords."""
        title = publication.get('title', '') or ''
        abstract = publication.get('abstract', '') or ''
        text_to_search = (title + ' ' + abstract).lower()
        
        categories = []
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_to_search:
                    categories.append(category)
                    break  # Only add category once
        
        return categories

    def load_existing_publications(self, category_file):
        """Load existing publications from a YAML file."""
        file_path = f"_data/{category_file}.yml"
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or []
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        return []

    def save_publications(self, category_file, publications):
        """Save publications to a YAML file."""
        file_path = f"_data/{category_file}.yml"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Sort by year (newest first)
        publications.sort(key=lambda x: x.get('year', 0), reverse=True)
        
        # Remove temporary fields before saving
        clean_publications = []
        for pub in publications:
            clean_pub = {k: v for k, v in pub.items() if k not in ['pmid', 'abstract', 'year']}
            clean_publications.append(clean_pub)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(clean_publications, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"Saved {len(clean_publications)} publications to {file_path}")
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def update_publications(self):
        """Main function to update all publications."""
        print("Starting PubMed scrape for Westover MB publications...")
        
        # Search for publications
        pmids = self.search_pubmed('Westover MB[Author]')
        
        if not pmids:
            print("No publications found!")
            return
        
        # Fetch detailed publication information
        publications = self.fetch_publication_details(pmids)
        
        if not publications:
            print("No publication details retrieved!")
            return
        
        print(f"Retrieved details for {len(publications)} publications")
        
        # Group publications by category
        category_publications = {}
        uncategorized = []
        
        for pub in publications:
            categories = self.categorize_publication(pub)
            
            if categories:
                for category in categories:
                    if category not in category_publications:
                        category_publications[category] = []
                    category_publications[category].append(pub)
            else:
                uncategorized.append(pub)
        
        # Update each category file
        for category, pubs in category_publications.items():
            # Load existing publications
            existing_pubs = self.load_existing_publications(category)
            
            # Merge with new publications (avoid duplicates by PMID)
            existing_pmids = set()
            for existing_pub in existing_pubs:
                # Extract PMID from URL if available. An entry's URL is either a
                # PubMed link or a cdac-downloads PDF named <...>_<PMID>.pdf --
                # both carry the PMID, and BOTH must be recognised here. If only
                # PubMed links were matched, every PDF-linked publication would
                # look "new" on each run and be re-appended nightly forever.
                if 'link' in existing_pub and 'url' in existing_pub['link']:
                    url = existing_pub['link']['url']
                    pmid_match = (re.search(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)', url)
                                  or PDF_PMID_RE.search(url))
                    if pmid_match:
                        existing_pmids.add(pmid_match.group(1))
            
            # Add new publications
            new_count = 0
            for pub in pubs:
                if pub['pmid'] not in existing_pmids:
                    existing_pubs.append(pub)
                    new_count += 1
            
            # Save updated publications
            if new_count > 0:
                self.save_publications(category, existing_pubs)
                print(f"Added {new_count} new publications to {category}")
            else:
                print(f"No new publications for {category}")
        
        # Report uncategorized publications
        if uncategorized:
            print(f"\n{len(uncategorized)} uncategorized publications:")
            for pub in uncategorized[:5]:  # Show first 5
                print(f"  - {pub['title']}")
            if len(uncategorized) > 5:
                print(f"  ... and {len(uncategorized) - 5} more")


def main():
    """Main function."""
    scraper = PubMedScraper()
    scraper.update_publications()
    print("Publication update complete!")


if __name__ == '__main__':
    main()