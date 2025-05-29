# Automated Publication Management

This repository now includes an automated system for keeping your publications page up to date by scraping PubMed for papers where you are listed as "Westover MB".

## How It Works

### Daily Automatic Updates
The system runs automatically every day at 2 AM UTC via GitHub Actions and:

1. **Searches PubMed** for all publications with "Westover MB[Author]"
2. **Categorizes publications** automatically based on keywords in titles and abstracts
3. **Updates YAML files** in `_data/` directory with new publications
4. **Avoids duplicates** by checking PMIDs against existing publications
5. **Commits changes** automatically if new publications are found

### Publication Categories

Publications are automatically sorted into these categories based on keyword matching:

- **Critical Care Neurophysiology**: ICU EEG, cEEG monitoring, seizure risk, IIIC patterns
- **Sleep Medicine**: Sleep staging, breathing, insomnia, brain age, spindles, dementia
- **Epilepsy**: Spike detection, seizure forecasting, epilepsy surgery
- **Machine Learning & AI**: Deep learning, neural networks, automated detection
- **Medical Informatics**: EHR phenotyping, NLP, risk prediction models
- **Computational Neuroscience**: Brain networks, connectivity, modeling
- **And many more...**

### Files

- `scrape_pubmed_auto.py` - Main scraping script
- `.github/workflows/sync-team-data.yml` - GitHub Actions workflow
- `_data/yaml*.yml` - Publication category files

## Manual Usage

To manually update publications:

```bash
# Install dependencies
pip install PyYAML

# Run the scraper
python scrape_pubmed_auto.py
```

## Customizing Categories

To add new categories or modify keyword matching:

1. Edit the `category_keywords` dictionary in `scrape_pubmed_auto.py`
2. Add new YAML file names and their associated keywords
3. The corresponding YAML files will be created automatically

Example:
```python
'yamlNewCategory': ['keyword1', 'keyword2', 'specific phrase'],
```

## Monitoring

- Check the **Actions** tab in GitHub to see sync results
- View **commit history** to see when new publications were added
- **Uncategorized publications** are reported in the action logs

## Publication Format

Each publication is stored with this structure:
```yaml
- title: "Publication Title"
  image: ''
  description: ''
  authors: Author1, Author2, Westover MB
  link:
    url: https://pubmed.ncbi.nlm.nih.gov/PMID
    display: Journal info with PMID
  highlight: 0
```

## API Usage

The system uses the NCBI E-utilities API which:
- Is free for reasonable use
- Has rate limiting (requests are spaced 0.5 seconds apart)
- Requires an email for identification (configured in the script)

## Troubleshooting

**No new publications found**: This is normal if you haven't published recently

**API errors**: Usually temporary - the system will retry the next day

**Wrong categorization**: Publications can appear in multiple categories if they match multiple keyword sets

**Missing publications**: Check if the author name format matches "Westover MB" in PubMed

## Benefits

✅ **Always up to date** - Publications appear automatically within 24 hours of PubMed indexing  
✅ **No manual work** - Completely automated categorization and formatting  
✅ **No duplicates** - Smart deduplication based on PMID  
✅ **Comprehensive** - Captures all publications, including recent ones  
✅ **Consistent formatting** - All publications follow the same YAML structure  

The system ensures your publications page stays current without any manual intervention!