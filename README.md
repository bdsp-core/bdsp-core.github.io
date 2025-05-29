# CCNL / BDSP Website

This is the website of our research group at Harvard Medical School / Beth Israel Deaconess Medical Center / Massachusetts General Hospital / Broad Institute.

## Overview

This Jekyll-based website serves as the digital presence for the Clinical Data Animation Center (CDAC) and Brain Data Science Platform (BDSP). The site includes information about our research, team members, publications, news, and resources.

## Features

- **Responsive Design**: Built with Bootstrap for mobile-friendly viewing
- **Dynamic Content**: Automatically synced data from Google Sheets and PubMed
- **Research Showcase**: Organized publications by research themes
- **Team Management**: Comprehensive team member profiles and roles
- **News & Updates**: Regular updates on lab activities and achievements

## Automated Data Synchronization

The website includes several automated processes that keep content up-to-date:

### Scheduled Jobs (Daily at 2 AM Eastern)

1. **Team Data Sync**: Updates team member information from Google Sheets
   - Syncs faculty, postdocs, students, staff, alumni, and collaborators
   - Updates photos, bios, roles, and contact information

2. **Quotes Sync**: Updates Brandon's quotes page from the CDAC_QUOTES Google Sheet
   - Organizes quotes by category with automatic table of contents
   - Maintains proper markdown formatting

3. **News Sync**: Updates lab news from Google Sheets
   - Chronological news feed with automatic date formatting

4. **Publications Sync**: Fetches latest publications from PubMed
   - Automatically categorizes by research themes
   - Updates publication counts and recent papers

### Manual Triggers

All automated jobs can also be triggered manually via GitHub Actions for immediate updates.

## File Structure

```
├── _data/           # YAML data files (team, publications, news)
├── _includes/       # Reusable HTML components
├── _layouts/        # Page templates
├── _pages/          # Main content pages
├── _sass/           # Styling (Bootstrap customization)
├── images/          # Static images and photos
├── .github/workflows/ # GitHub Actions for automation
├── sync_*.py        # Data synchronization scripts
└── scrapeNCBI/      # PubMed scraping utilities
```

## Local Development

1. Install Jekyll and dependencies:
   ```bash
   gem install bundler jekyll
   bundle install
   ```

2. Run locally:
   ```bash
   bundle exec jekyll serve
   ```

3. View at `http://localhost:4000`

## Data Sources & Content Management

### External Data Sources (Automatically Synced)

1. **Google Sheets**
   - **Team Data**: Faculty, postdocs, students, staff, alumni, and collaborator information
   - **CDAC_QUOTES**: Brandon's quote collection organized by category  
   - **News**: Lab announcements, achievements, and updates

2. **PubMed/NCBI**: Research publications automatically categorized by research themes

### Local Content Storage

#### Images (`/images/`)

- **`logopic/`**: Institutional logos (HMS, MGH, BIDMC, Broad Institute, etc.)
- **`teampic/`**: Team member photos and headshots
  - Individual photos for faculty, students, staff
  - Original backup copies in `original_backup/` subdirectory
- **`picpic/`**: Lab photos and social events
  - **`Gallery/`**: Photo gallery for lab activities, conferences, social events
- **`pubpic/`**: Publication-related images and figures
- **`respic/`**: Research-related graphics and animations
- **`slider7001400/`**: Homepage carousel images (research highlights)
  - Includes resized versions and `originals/` subdirectory
- **`newspic/`**: News and announcement related images

#### Downloadable Content (`/downloads/`)

- **Research Papers**: PDFs of key publications (numbered 1-11+)
- **CV**: Brandon's academic CV
- **Guidelines & Protocols**: 
  - ICU-EEG monitoring protocols
  - CONSORT diagrams
  - TRIPOD checklists
- **Presentations**: Conference presentations (IFCN, etc.)
- **Documentation**: User guides, methodology papers
- **Manuscripts**: Working drafts and submissions

#### Structured Data (`/_data/`)

**Team Information:**
- `faculty.yml`: Faculty member profiles
- `postdocsStudentsStaff.yml`: Current lab members  
- `alumni.yml`: Former lab members
- `collaborators.yml`: External collaborators
- `engineering.yml`: Technical staff and engineers

**Publications (Research Theme Categories):**
- `publist.yml`: Main publication list
- Theme-specific YAML files:
  - `yamlML_AI.yml`: Machine learning and AI
  - `yamleeg.yml`: EEG-related research
  - `yamlseizures.yml`: Seizure detection/prediction
  - `yamlsleepStaging.yml`: Sleep research
  - `yamlcEEG.yml`: Continuous EEG monitoring
  - `yamlbrainAge.yml`: Brain age modeling
  - `yamlcovid.yml`: COVID-19 related studies
  - `yamlcardiacArrest.yml`: Cardiac arrest outcomes
  - `yamlSAH.yml`: Subarachnoid hemorrhage
  - `yamldelirium.yml`: Delirium assessment
  - And 20+ other specialized research themes

**Other Data:**
- `news.yml`: Lab news and announcements
- `pictures_CCNL.yml`: Photo gallery metadata
- `wordCloudAbstracts.txt`: Text for generating word clouds

### Content Update Methods

- **Automated (Daily)**: Team data, quotes, news from Google Sheets; publications from PubMed
- **Manual**: Static pages, images, downloadable content, theme categorizations
- **Semi-automated**: Publication theme tagging (manual tagging, automatic organization)

## GitHub Pages Deployment

The site is automatically deployed to GitHub Pages on every push to the `gh-pages` branch. The automated sync jobs also commit changes directly to this branch.

## Credits

Website design originally based on the Allan Lab template (http://www.allanlab.org/). 
Heavily modified and enhanced for the CDAC/BDSP research group needs.

## License

Copyright CDAC. Code released under the MIT License.
