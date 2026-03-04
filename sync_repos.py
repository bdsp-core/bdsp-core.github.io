#!/usr/bin/env python3
"""
Sync GitHub repository metadata for the bdsp-core organization.

This script:
1. Fetches all repos (public + private) from the bdsp-core GitHub org
2. Maps each repo to a research category
3. Writes _data/repos.yml for the Jekyll site to render

Requires: GITHUB_TOKEN env var (PAT with org repo read access for private repos)
"""

import os
import json
import re
import yaml
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError


# ============================================================
# CATEGORY MAPPING
# To add a new repo: add its exact GitHub name as a key below.
# To add a new category: add a new value string + update CATEGORY_ORDER.
# Repos not listed here will appear under "Uncategorized".
# ============================================================

REPO_CATEGORIES = {
    # --- Sleep Staging & Sleep AI ---
    "sleep_staging_2000pts": "Sleep Staging & Sleep AI",
    "ecg_respiration_sleep_staging": "Sleep Staging & Sleep AI",
    "ecg_respiration_sleep_staging_icu": "Sleep Staging & Sleep AI",
    "Ordinal-Sleep-Depth": "Sleep Staging & Sleep AI",
    "outcome-oriented-sleep-staging": "Sleep Staging & Sleep AI",
    "sleep_staging_tl_scorability": "Sleep Staging & Sleep AI",
    "PANDA-Sleep": "Sleep Staging & Sleep AI",
    "BCH-PSG-dataset": "Sleep Staging & Sleep AI",
    "bdsp-sleep-data": "Sleep Staging & Sleep AI",
    "Physionet2018_Challenge_Submission": "Sleep Staging & Sleep AI",
    "sleep-outcome-prediction": "Sleep Staging & Sleep AI",
    "sleep_eeg_age_norm": "Sleep Staging & Sleep AI",
    "CAISR-App": "Sleep Staging & Sleep AI",
    "AFib-sleep-cognition": "Sleep Staging & Sleep AI",
    "spindle_optimization": "Sleep Staging & Sleep AI",
    # Likely private:
    "SleepBreathing-DL": "Sleep Staging & Sleep AI",
    "AirGo_SleepStaging": "Sleep Staging & Sleep AI",
    "AirGoSleepPyT0-": "Sleep Staging & Sleep AI",
    "sleep_research_io": "Sleep Staging & Sleep AI",
    "spindle_detection": "Sleep Staging & Sleep AI",
    "AirGo_ApneaDetection": "Sleep Staging & Sleep AI",
    "Undiagnosed_Apnea": "Sleep Staging & Sleep AI",
    "Auto_PSG_Respiration": "Sleep Staging & Sleep AI",
    "CAISR_might_be_junk": "Sleep Staging & Sleep AI",
    "ICU-sleep-vitals": "Sleep Staging & Sleep AI",
    "sleep_general": "Sleep Staging & Sleep AI",
    "self-similarity-dev": "Sleep Staging & Sleep AI",
    "sleep_cognition": "Sleep Staging & Sleep AI",
    "Sleep-deidentification": "Sleep Staging & Sleep AI",
    "sleep_eeg_mri": "Sleep Staging & Sleep AI",
    "caisr_dev": "Sleep Staging & Sleep AI",
    "CAISR": "Sleep Staging & Sleep AI",
    "CAISR2": "Sleep Staging & Sleep AI",
    "sleep-conversion": "Sleep Staging & Sleep AI",
    "BCH-Sleep-Step1": "Sleep Staging & Sleep AI",
    "koges_sleep_staging": "Sleep Staging & Sleep AI",
    "ICU-Sleep": "Sleep Staging & Sleep AI",
    "noiselight": "Sleep Staging & Sleep AI",

    # --- Brain Age & Brain Health ---
    "philosophers-stone": "Brain Age & Brain Health",
    "SleepEEGBasedBrainAge": "Brain Age & Brain Health",
    "BrainHealthExercise_Dataset": "Brain Age & Brain Health",
    "meditation-sleep-brain-age": "Brain Age & Brain Health",
    "BigBrainImagingDatabase": "Brain Age & Brain Health",
    "mri-cognition-eeg-wei2024": "Brain Age & Brain Health",
    "HIV-BAI": "Brain Age & Brain Health",
    "BAI-EPILEPSY": "Brain Age & Brain Health",
    # Likely private:
    "BrainAgeExercise": "Brain Age & Brain Health",

    # --- Breathing & Respiratory ---
    "breathing-stability-index": "Breathing & Respiratory",
    "self_similarity": "Breathing & Respiratory",
    "respiratory_event_detection_wearable": "Breathing & Respiratory",
    "Morphological-Prediction-of-CPAP-Associated-Acute-Respiratory-Instability": "Breathing & Respiratory",
    "HLG_Mackey-Glass": "Breathing & Respiratory",

    # --- Seizures, IIIC Patterns & Spike Detection ---
    "IIIC-SPaRCNet": "Seizures, IIIC Patterns & Spike Detection",
    "IIIC-Frequency-Analysis": "Seizures, IIIC Patterns & Spike Detection",
    "IIIC-Frequency-Analysis-2": "Seizures, IIIC Patterns & Spike Detection",
    "IIIC-IRR": "Seizures, IIIC Patterns & Spike Detection",
    "Seizures-and-Harmful-Brain-Activity": "Seizures, IIIC Patterns & Spike Detection",
    "seizure_forecasting_crash_analysis": "Seizures, IIIC Patterns & Spike Detection",
    "TEEGLLTEEG": "Seizures, IIIC Patterns & Spike Detection",
    "morgoth": "Seizures, IIIC Patterns & Spike Detection",
    "cyclops": "Seizures, IIIC Patterns & Spike Detection",
    "timeline-viewer": "Seizures, IIIC Patterns & Spike Detection",
    "SpikeNet1": "Seizures, IIIC Patterns & Spike Detection",
    "SpikeNet2": "Seizures, IIIC Patterns & Spike Detection",
    "spike-test-pilot-trial": "Seizures, IIIC Patterns & Spike Detection",
    "IFCN6": "Seizures, IIIC Patterns & Spike Detection",
    "Rapid_IIIC_Labeling_GUI": "Seizures, IIIC Patterns & Spike Detection",
    # Likely private:
    "AL_IIIC": "Seizures, IIIC Patterns & Spike Detection",
    "IIIC_big_map": "Seizures, IIIC Patterns & Spike Detection",
    "epilepsy-project": "Seizures, IIIC Patterns & Spike Detection",
    "EEG-Pipeline": "Seizures, IIIC Patterns & Spike Detection",
    "Rapid_IIIC_Labeling_GUI_MultipleEEGs": "Seizures, IIIC Patterns & Spike Detection",
    "eeg_multitask_embedding": "Seizures, IIIC Patterns & Spike Detection",
    "Burst-Suppression-Segmentation": "Seizures, IIIC Patterns & Spike Detection",

    # --- Delirium, Encephalopathy & CAR-T Neurotoxicity ---
    "E-CAM-S": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "VE-CAM-S": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "rass_delirium_eeg_prediction": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "kimchi_delirium_2019": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "EGG-IRR-1.0": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "irr-aware-eeg": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "VE-ICANS": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "E-ICANS": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "ICANS-forecasting-after-CAR-T-cell-therapy": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    # Likely private:
    "delirium-nlp-colaboration": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "MGHNursingCAMsDataset": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "DeliriumToDementia_CausalSurvivalAnalysis": "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "IIC_DTR": "Delirium, Encephalopathy & CAR-T Neurotoxicity",

    # --- ICU & Critical Care ---
    "icare-dl": "ICU & Critical Care",
    "Hypothermia-EEG": "ICU & Critical Care",
    "cdac-burst-suppression-data": "ICU & Critical Care",
    "ICU_EEG_Neuro_Prognosis": "ICU & Critical Care",
    "SAH_DCI_Prediction_EEG": "ICU & Critical Care",
    "SAH-Annals-2018": "ICU & Critical Care",
    "IMPS": "ICU & Critical Care",
    "covid_acuity_score": "ICU & Critical Care",
    "ADARRI": "ICU & Critical Care",
    "EEG_mulitmodal_sedation": "ICU & Critical Care",
    # Likely private:
    "SOFA": "ICU & Critical Care",
    "SOFA-LR": "ICU & Critical Care",
    "icare-dl-lstm": "ICU & Critical Care",
    "pkpd-causal-matching": "ICU & Critical Care",
    "time-varying-causal-inference-simulation-tutorial": "ICU & Critical Care",
    "MOCA": "ICU & Critical Care",
    "ABIEE": "ICU & Critical Care",
    "CCI_SOFA": "ICU & Critical Care",
    "Covid19_Respiration": "ICU & Critical Care",

    # --- EHR Phenotyping & Clinical NLP ---
    "NIDX": "EHR Phenotyping & Clinical NLP",
    "NAX-Epilepsy": "EHR Phenotyping & Clinical NLP",
    "NAX-MCI-AD": "EHR Phenotyping & Clinical NLP",
    "NAX-Narcolepsy": "EHR Phenotyping & Clinical NLP",
    "NAX-Parkinsons": "EHR Phenotyping & Clinical NLP",
    "SDH-EHR-Phenotyping-NAX": "EHR Phenotyping & Clinical NLP",
    "CRIME-PISE": "EHR Phenotyping & Clinical NLP",
    # Likely private:
    "EHR-phenotyping-NAX": "EHR Phenotyping & Clinical NLP",
    "NLP_GUI": "EHR Phenotyping & Clinical NLP",
    "ELUCID": "EHR Phenotyping & Clinical NLP",

    # --- Noise & Diagnostic Variability ---
    "Noise-in-Diagnosing-Epilepsy": "Noise & Diagnostic Variability",
    "Noise_in_Diagnosing_Epilepsy": "Noise & Diagnostic Variability",

    # --- Data Platforms & Infrastructure ---
    "bdsp-core.github.io": "Data Platforms & Infrastructure",
    "bdsp-reports-opensearch": "Data Platforms & Infrastructure",
    "bdsp-license-and-dua": "Data Platforms & Infrastructure",
    "awesome-aws-research": "Data Platforms & Infrastructure",
    "aws-open-data-registry": "Data Platforms & Infrastructure",
    "aws-open-data-registry-browser": "Data Platforms & Infrastructure",
    "Physionet_build_forked": "Data Platforms & Infrastructure",
    "epilepsy-algolia-sync": "Data Platforms & Infrastructure",
    "Harvard-EEG-Database-Tools": "Data Platforms & Infrastructure",
    "plot-ecg": "Data Platforms & Infrastructure",
    # Likely private:
    "Bedmaster-ICU-tools": "Data Platforms & Infrastructure",
    "CDAC_Data_Portal": "Data Platforms & Infrastructure",
    "text-annotator": "Data Platforms & Infrastructure",
    "bedmaster_pipeline_code": "Data Platforms & Infrastructure",
    "streaming_pipeline_code": "Data Platforms & Infrastructure",
    "Bedmaster-Patient-Matching": "Data Platforms & Infrastructure",
    "general-scripts": "Data Platforms & Infrastructure",
    "DailyUpdates": "Data Platforms & Infrastructure",
    "dicom_deidentify": "Data Platforms & Infrastructure",
    "ECG-deidentification-pipeline": "Data Platforms & Infrastructure",
    "EEG-Archiving-Pipeline": "Data Platforms & Infrastructure",
    "EEGNormalization": "Data Platforms & Infrastructure",
    "EEG_Fuzzy_Patient_Matching": "Data Platforms & Infrastructure",
    "Xltek_Annotation_Extraction": "Data Platforms & Infrastructure",
    "Persyst_Spike_Detection": "Data Platforms & Infrastructure",
    "EEG-deidentification": "Data Platforms & Infrastructure",
    "BDSPAWSScripts": "Data Platforms & Infrastructure",
    "bdsp-opendata-registry": "Data Platforms & Infrastructure",
    "GeneralScripts": "Data Platforms & Infrastructure",
    "ECG_HD5_Plots": "Data Platforms & Infrastructure",
    "bdsp.io_webapp": "Data Platforms & Infrastructure",
    "delphi-deidentification": "Data Platforms & Infrastructure",
    "bdsp-emr-tools": "Data Platforms & Infrastructure",
    "bdsp-boto3-example": "Data Platforms & Infrastructure",
    "bdsp-reports-search-web-app": "Data Platforms & Infrastructure",
    "bdsp_aws_athena_db_connection_code": "Data Platforms & Infrastructure",
    "EEG-Archiving-Pipeline-BIDMC": "Data Platforms & Infrastructure",
    "BIDS-EEG": "Data Platforms & Infrastructure",
    "BIDS-Conversion": "Data Platforms & Infrastructure",
    "BIDMCDatabase": "Data Platforms & Infrastructure",
    "BIDS_Conversion": "Data Platforms & Infrastructure",
    "EEG-Indexing-Pipeline": "Data Platforms & Infrastructure",
    "Sleep-Indexing-Pipeline": "Data Platforms & Infrastructure",
    "medications_mgh": "Data Platforms & Infrastructure",
    "philter-plus-deidentification": "Data Platforms & Infrastructure",
    "MGB-Neurology-Reports-Deidentification": "Data Platforms & Infrastructure",
    "BIDMC-EEG-Reports-Deidentification": "Data Platforms & Infrastructure",
    "natus2json": "Data Platforms & Infrastructure",
    "MGB-Notes-Deidentification": "Data Platforms & Infrastructure",
    "Thunderpack": "Data Platforms & Infrastructure",
    "IDEA_Platform_MGB": "Data Platforms & Infrastructure",
    "BDSP_BIDS_Conversion_withAnnotationStaging_from_XLTEK_raw": "Data Platforms & Infrastructure",
    "BIDMC-Notes-Deidentification": "Data Platforms & Infrastructure",
    "Imaging-Reports-Deidentification": "Data Platforms & Infrastructure",
    "PHIlter-deID-pipeline-mbw-modified": "Data Platforms & Infrastructure",
    "Thunderpack_WranglingCode": "Data Platforms & Infrastructure",
    "edfio": "Data Platforms & Infrastructure",
    "BIDS_EDF_to_BidsFormat_Conversion": "Data Platforms & Infrastructure",
    "BIDS_Sessions_Creations": "Data Platforms & Infrastructure",
    "EEGReportsDeidentification": "Data Platforms & Infrastructure",
    "EEG_Report_Wrangling": "Data Platforms & Infrastructure",
    "LabMeetingDemo": "Data Platforms & Infrastructure",
    "ECG-Philter-DeIdentification": "Data Platforms & Infrastructure",
    "interrater_analysis": "Data Platforms & Infrastructure",
    "cdac_google": "Data Platforms & Infrastructure",
    "tensorizer": "Data Platforms & Infrastructure",
    "mbw-zettelkasten": "Data Platforms & Infrastructure",
    "Omega": "Data Platforms & Infrastructure",

    # --- Newly discovered private repos (from workflow run) ---
    # Sleep
    "BCH-SleepStaging": "Sleep Staging & Sleep AI",
    "CAISR_internal": "Sleep Staging & Sleep AI",
    "frankenstein-sleep": "Sleep Staging & Sleep AI",
    "ICU_SLEEP": "Sleep Staging & Sleep AI",
    "sleep-clinic-tools": "Sleep Staging & Sleep AI",
    "sleep-philosophers-stone": "Sleep Staging & Sleep AI",
    "sleep-yoda": "Sleep Staging & Sleep AI",
    "spin": "Sleep Staging & Sleep AI",

    # Brain Age & Brain Health
    "brain_age_koges": "Brain Age & Brain Health",
    "AD-PD-EEG": "Brain Age & Brain Health",
    "Whole-Brain-Modeling": "Brain Age & Brain Health",

    # Breathing & Respiratory
    "breathing_stability_index": "Breathing & Respiratory",

    # Seizures, IIIC Patterns & Spike Detection
    "Epilepsy_Detection_Lr": "Seizures, IIIC Patterns & Spike Detection",
    "morgoth-viewer": "Seizures, IIIC Patterns & Spike Detection",
    "saurons_eye": "Seizures, IIIC Patterns & Spike Detection",
    "prophet": "Seizures, IIIC Patterns & Spike Detection",
    "ISR-IRR": "Seizures, IIIC Patterns & Spike Detection",

    # Delirium, Encephalopathy & CAR-T Neurotoxicity
    "muse": "Delirium, Encephalopathy & CAR-T Neurotoxicity",

    # ICU & Critical Care
    "ICU_EEG_PKPD_EmulatedTrial": "ICU & Critical Care",
    "ICU_EEG_PKPD_SIMS": "ICU & Critical Care",
    "ECGFounder": "ICU & Critical Care",

    # EHR Phenotyping & Clinical NLP
    "NAX-BrainTumors": "EHR Phenotyping & Clinical NLP",
    "NAX-CardiacArrest": "EHR Phenotyping & Clinical NLP",
    "NAX-HemorrhagicStroke": "EHR Phenotyping & Clinical NLP",
    "NAX-Ischemic-Stroke": "EHR Phenotyping & Clinical NLP",
    "NAX-SAH": "EHR Phenotyping & Clinical NLP",
    "NAX-TBI": "EHR Phenotyping & Clinical NLP",

    # Data Platforms & Infrastructure
    "bdsp.io_webapp_dev": "Data Platforms & Infrastructure",
    "bdsp.io_webapp_prod": "Data Platforms & Infrastructure",
    "bdsp_bidmc": "Data Platforms & Infrastructure",
    "BIDS_Annotations_Deidentification": "Data Platforms & Infrastructure",
    "BIDS_Cleanup_delete_no_edf_sessions": "Data Platforms & Infrastructure",
    "BIDS_EDF_to_BidsFormat_Conversion_EMORY": "Data Platforms & Infrastructure",
    "BIDS_EDF_to_BidsFormat_Conversion_STANFORD": "Data Platforms & Infrastructure",
    "BIDS_StartTime_Extraction": "Data Platforms & Infrastructure",
    "discontinuous-edf-to-bids-": "Data Platforms & Infrastructure",
    "MGBNatusToBIDSConversion": "Data Platforms & Infrastructure",
    "demo-repository": "Data Platforms & Infrastructure",
    "brandons-labyrinth": "Data Platforms & Infrastructure",
    "grant-banana": "Data Platforms & Infrastructure",
    "YAMA": "Data Platforms & Infrastructure",
}

# Controls the display order of categories on the page
CATEGORY_ORDER = [
    "Sleep Staging & Sleep AI",
    "Brain Age & Brain Health",
    "Breathing & Respiratory",
    "Seizures, IIIC Patterns & Spike Detection",
    "Delirium, Encephalopathy & CAR-T Neurotoxicity",
    "ICU & Critical Care",
    "EHR Phenotyping & Clinical NLP",
    "Noise & Diagnostic Variability",
    "Data Platforms & Infrastructure",
    "Uncategorized",
]

ORG_NAME = "bdsp-core"
OUTPUT_FILE = "_data/repos.yml"


def make_slug(text):
    """Convert category name to a URL-safe slug for HTML IDs."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug).strip('-')
    return slug


def fetch_all_repos():
    """Fetch all repos from the GitHub org, handling pagination."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "bdsp-core-website-sync",
    }

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("ORG_PAT")
    if token:
        headers["Authorization"] = f"token {token}"
        print("Using authenticated GitHub API access.")
    else:
        print("WARNING: No GITHUB_TOKEN set. Only public repos will be fetched.")

    all_repos = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/orgs/{ORG_NAME}/repos"
            f"?per_page=100&page={page}&type=all&sort=full_name"
        )
        req = Request(url, headers=headers)

        try:
            with urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            print(f"ERROR: GitHub API returned {e.code}: {e.reason}")
            if e.code == 401:
                print("Authentication failed. Check your GITHUB_TOKEN / ORG_PAT.")
            elif e.code == 403:
                print("Rate limit or permission issue. Try again later or use a token.")
            return None

        if not data:
            break

        all_repos.extend(data)
        print(f"  Fetched page {page}: {len(data)} repos")

        if len(data) < 100:
            break
        page += 1

    return all_repos


def process_repos(raw_repos):
    """Transform raw GitHub API data into our YAML structure."""
    repos = []

    for r in raw_repos:
        name = r["name"]
        category = REPO_CATEGORIES.get(name, "Uncategorized")

        try:
            sort_order = CATEGORY_ORDER.index(category)
        except ValueError:
            sort_order = len(CATEGORY_ORDER)

        # Parse updated_at to just the date
        updated = r.get("updated_at", "")
        if updated:
            try:
                updated = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            except ValueError:
                updated = updated[:10]

        repos.append({
            "name": name,
            "description": r.get("description") or "No description provided.",
            "url": r.get("html_url", f"https://github.com/{ORG_NAME}/{name}"),
            "language": r.get("language") or "",
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "updated_at": updated,
            "visibility": r.get("visibility", "public"),
            "category": category,
            "category_slug": make_slug(category),
            "topics": r.get("topics", []),
            "sort_order": sort_order,
        })

    # Sort by category order, then alphabetically by name within each category
    repos.sort(key=lambda x: (x["sort_order"], x["name"].lower()))

    return repos


def print_summary(repos):
    """Print a summary of categorized repos."""
    from collections import Counter
    cat_counts = Counter(r["category"] for r in repos)

    print(f"\n{'=' * 50}")
    print(f"Total repos: {len(repos)}")
    print(f"{'=' * 50}")

    for cat in CATEGORY_ORDER:
        count = cat_counts.get(cat, 0)
        if count > 0:
            print(f"  {cat}: {count}")

    uncategorized = [r["name"] for r in repos if r["category"] == "Uncategorized"]
    if uncategorized:
        print(f"\nUncategorized repos ({len(uncategorized)}):")
        for name in sorted(uncategorized):
            print(f"  - {name}")
        print("Add these to REPO_CATEGORIES in sync_repos.py to assign them.")


def main():
    print(f"Fetching repos for {ORG_NAME}...")
    raw_repos = fetch_all_repos()

    if raw_repos is None:
        print("Failed to fetch repos. Keeping existing data.")
        return

    print(f"\nFetched {len(raw_repos)} total repos.")

    repos = process_repos(raw_repos)
    print_summary(repos)

    # Write YAML
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(repos, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\nWrote {len(repos)} repos to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
