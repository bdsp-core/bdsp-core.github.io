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
import base64
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
    # --- Manually assigned (May 2026 cleanup pass) ---
    "bai-dementia": "Brain Age & Brain Health",
    "dementia-detection-from-sleep": "Brain Age & Brain Health",
    "sleep-phenomics-automation": "Sleep Staging & Sleep AI",
    "grond": "Seizures, IIIC Patterns & Spike Detection",
    "hrv-tools": "ICU & Critical Care",
    "nax-gcs": "ICU & Critical Care",
    "cdac-downloads": "Data Platforms & Infrastructure",
    "paper-agents-figures": "Research Tools & Manuscript AI",
    "paper-agents-manuscript": "Research Tools & Manuscript AI",
    "PAT-PaperAssessmentTool": "Research Tools & Manuscript AI",

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

# ============================================================
# DESCRIPTION OVERRIDES
# If a repo has no GitHub "About" description, this dict provides one.
# These take effect only when the GitHub description is empty/null.
# To force-override a GitHub description, prefix with "!" (not implemented yet).
# ============================================================

REPO_DESCRIPTIONS = {
    # --- Sleep Staging & Sleep AI ---
    "AFib-sleep-cognition": "Atrial fibrillation detection during sleep and its relationship to cognitive outcomes.",
    "BCH-PSG-dataset": "Boston Children's Hospital polysomnography dataset for pediatric sleep research.",
    "BCH-SleepStaging": "Sleep staging models for Boston Children's Hospital polysomnography data.",
    "Ordinal-Sleep-Depth": "Ordinal regression models for continuous sleep depth estimation from EEG.",
    "PANDA-Sleep": "PANDA deep learning framework for automated sleep staging across pediatric and adult populations.",
    "Sleep-deidentification": "De-identification pipeline for sleep study recordings.",
    "ecg_respiration_sleep_staging": "Sleep staging using ECG-derived respiration signals.",
    "frankenstein-sleep": "Multi-source sleep staging model combining heterogeneous EEG datasets.",
    "koges_sleep_staging": "Sleep staging analysis for Korean Genome and Epidemiology Study (KoGES) cohort.",
    "outcome-oriented-sleep-staging": "Sleep staging optimized for clinical outcome prediction rather than epoch-level accuracy.",
    "sleep-clinic-tools": "Clinical tools and utilities for sleep medicine practice.",
    "sleep-outcome-prediction": "Predicting clinical outcomes from sleep study features and polysomnography data.",
    "sleep-yoda": "YODA (Your Optimized Data Analyzer) framework for sleep data analysis.",
    "sleep_eeg_age_norm": "Age-based normative values for sleep EEG parameters across the lifespan.",
    "sleep_staging_2000pts": "Automated sleep staging model trained and validated on 2,000 patients.",
    "spindle_detection": "Automated detection of sleep spindles from EEG recordings.",
    "spindle_optimization": "Optimization of sleep spindle detection algorithms and parameters.",
    "ICU_SLEEP": "Sleep analysis tools for ICU patient EEG recordings.",
    "CAISR_internal": "Internal development repository for CAISR sleep analysis platform.",

    # --- Brain Age & Brain Health ---
    "BAI-EPILEPSY": "Brain Age Index analysis in epilepsy patients to quantify neurodegeneration.",
    "BigBrainImagingDatabase": "Large-scale brain imaging database for multi-modal neurological research.",
    "BrainAgeExercise": "Effects of physical exercise on brain age as measured by EEG biomarkers.",
    "BrainHealthExercise_Dataset": "Dataset for studying exercise effects on brain health metrics.",
    "HIV-BAI": "Brain Age Index analysis in HIV patients to assess neurocognitive impact.",
    "SleepEEGBasedBrainAge": "Brain age estimation from sleep EEG recordings using deep learning.",
    "brain_age_koges": "Brain age estimation for Korean Genome and Epidemiology Study (KoGES) cohort.",
    "Whole-Brain-Modeling": "Computational whole-brain modeling and simulation of neural dynamics.",
    "AD-PD-EEG": "EEG-based biomarkers for Alzheimer's disease and Parkinson's disease.",

    # --- Breathing & Respiratory ---
    "HLG_Mackey-Glass": "Hurst-Ljapunov-Grassberger analysis using Mackey-Glass equations for respiratory signal dynamics.",
    "Morphological-Prediction-of-CPAP-Associated-Acute-Respiratory-Instability": "Predicting acute respiratory instability from CPAP waveform morphology.",
    "breathing_stability_index": "Computing the breathing stability index from respiratory signals.",

    # --- Seizures, IIIC Patterns & Spike Detection ---
    "AL_IIIC": "Active learning framework for IIIC (ictal-interictal-injury continuum) pattern classification.",
    "Burst-Suppression-Segmentation": "Automated segmentation of burst-suppression patterns in EEG.",
    "EEG-Pipeline": "Processing pipeline for EEG seizure and pattern analysis.",
    "Epilepsy_Detection_Lr": "Logistic regression models for epilepsy detection from EEG features.",
    "IIIC-SPaRCNet": "SPaRCNet deep learning model for classifying IIIC patterns on EEG.",
    "IIIC_big_map": "Large-scale mapping and visualization of IIIC patterns across patient populations.",
    "ISR-IRR": "Inter-scorer reliability and inter-rater reliability analysis for EEG interpretation.",
    "Rapid_IIIC_Labeling_GUI": "GUI tool for rapid labeling of IIIC patterns on EEG recordings.",
    "Seizures-and-Harmful-Brain-Activity": "Detection and classification of seizures and harmful brain activity patterns on EEG.",
    "SpikeNet1": "Deep learning model for automated interictal epileptiform spike detection (version 1).",
    "SpikeNet2": "Deep learning model for automated interictal epileptiform spike detection (version 2).",
    "cyclops": "EEG seizure detection and continuous monitoring analysis tool.",
    "eeg_multitask_embedding": "Multi-task learning embeddings for EEG seizure and pattern classification.",
    "morgoth": "Deep learning framework for EEG pattern classification and seizure detection.",
    "morgoth-viewer": "Visualization tool for Morgoth EEG pattern classification results.",
    "prophet": "Seizure prediction and forecasting model using EEG data.",
    "saurons_eye": "Real-time EEG monitoring and pattern detection system.",
    "seizure_forecasting_crash_analysis": "Analysis of seizure forecasting model failures and edge cases.",
    "spike-test-pilot-trial": "Pilot clinical trial for validating automated spike detection systems.",
    "timeline-viewer": "Interactive timeline viewer for EEG events, seizures, and clinical annotations.",

    # --- Delirium, Encephalopathy & CAR-T Neurotoxicity ---
    "DeliriumToDementia_CausalSurvivalAnalysis": "Causal survival analysis of delirium progression to dementia.",
    "E-ICANS": "EEG-based assessment of Immune Effector Cell-Associated Neurotoxicity Syndrome (ICANS).",
    "IIC_DTR": "Dynamic treatment regimes for ictal-interictal continuum pattern management.",
    "MGHNursingCAMsDataset": "Massachusetts General Hospital nursing Confusion Assessment Method (CAM) dataset.",
    "delirium-nlp-colaboration": "NLP-based delirium detection and phenotyping from clinical notes.",
    "kimchi_delirium_2019": "EEG-based delirium prediction models (Kimchi et al., 2019).",
    "muse": "Multi-modal understanding of sedation and encephalopathy in ICU patients.",
    "rass_delirium_eeg_prediction": "RASS-based delirium prediction using EEG features.",

    # --- ICU & Critical Care ---
    "ABIEE": "Acute Brain Injury EEG Evaluation tools and analysis pipelines.",
    "EEG_mulitmodal_sedation": "Multimodal EEG analysis for sedation level monitoring in ICU patients.",
    "ECGFounder": "Foundation model for ECG analysis in critical care settings.",
    "Hypothermia-EEG": "EEG analysis during therapeutic hypothermia in post-cardiac arrest ICU patients.",
    "ICU_EEG_Neuro_Prognosis": "EEG-based neurological prognostication for ICU patients.",
    "ICU_EEG_PKPD_EmulatedTrial": "Emulated clinical trial for ICU EEG pharmacokinetic-pharmacodynamic analysis.",
    "ICU_EEG_PKPD_SIMS": "Simulation framework for ICU EEG pharmacokinetic-pharmacodynamic modeling.",
    "icare-dl-lstm": "LSTM deep learning models for the ICARE (International Cardiac Arrest Registry) study.",
    "pkpd-causal-matching": "Causal matching methods for pharmacokinetic-pharmacodynamic studies in ICU.",
    "time-varying-causal-inference-simulation-tutorial": "Tutorial on time-varying causal inference methods with simulation examples for ICU data.",

    # --- EHR Phenotyping & Clinical NLP ---
    "CRIME-PISE": "CRIME-PISE algorithm for clinical phenotyping from electronic health records.",
    "EHR-phenotyping-NAX": "Shared NAX framework and tools for EHR-based phenotyping.",
    "ELUCID": "EHR-based clinical data integration and phenotyping platform.",
    "NAX-BrainTumors": "NAX algorithm for automated brain tumor phenotyping from clinical notes.",
    "NAX-Epilepsy": "NAX algorithm for automated epilepsy phenotyping from clinical notes.",
    "NAX-HemorrhagicStroke": "NAX algorithm for hemorrhagic stroke phenotyping from clinical notes.",
    "NAX-Ischemic-Stroke": "NAX algorithm for ischemic stroke phenotyping from clinical notes.",
    "NAX-MCI-AD": "NAX algorithm for mild cognitive impairment and Alzheimer's disease phenotyping.",
    "NAX-Narcolepsy": "NAX algorithm for automated narcolepsy phenotyping from clinical notes.",
    "NAX-Parkinsons": "NAX algorithm for automated Parkinson's disease phenotyping from clinical notes.",
    "NAX-SAH": "NAX algorithm for subarachnoid hemorrhage phenotyping from clinical notes.",
    "NAX-TBI": "NAX algorithm for traumatic brain injury phenotyping from clinical notes.",
    "NLP_GUI": "GUI tool for clinical NLP annotation and review.",
    "SDH-EHR-Phenotyping-NAX": "NAX-based phenotyping for subdural hematoma from EHR data.",

    # --- Data Platforms & Infrastructure ---
    "BDSPAWSScripts": "AWS automation scripts for BDSP cloud infrastructure.",
    "BDSP_BIDS_Conversion_withAnnotationStaging_from_XLTEK_raw": "Pipeline converting raw XLTEK EEG files with annotations to BIDS format.",
    "BIDS-EEG": "EEG data conversion and management tools using BIDS standard.",
    "BIDS_Annotations_Deidentification": "De-identification of annotations in BIDS-formatted EEG datasets.",
    "BIDS_Cleanup_delete_no_edf_sessions": "Cleanup tool to remove BIDS sessions lacking EDF files.",
    "BIDS_Conversion": "General-purpose EEG-to-BIDS format conversion tools.",
    "BIDS_EDF_to_BidsFormat_Conversion": "Pipeline for converting EDF files to BIDS format.",
    "BIDS_EDF_to_BidsFormat_Conversion_STANFORD": "Stanford-specific pipeline for EDF-to-BIDS conversion.",
    "BIDS_Sessions_Creations": "Tools for creating and managing BIDS session structures.",
    "BIDS_StartTime_Extraction": "Extracting recording start times for BIDS metadata.",
    "CDAC_Data_Portal": "Clinical Data Animations Center (CDAC) web portal for data access.",
    "ECG-deidentification-pipeline": "Pipeline for de-identifying ECG recordings.",
    "ECG_HD5_Plots": "Plotting tools for ECG data stored in HDF5 format.",
    "EEG-deidentification": "De-identification pipeline for EEG recordings to remove PHI.",
    "EEGNormalization": "Tools for normalizing EEG signal data across datasets.",
    "EEG_Fuzzy_Patient_Matching": "Fuzzy matching algorithms for linking EEG records to patient identities.",
    "EEG_Report_Wrangling": "Tools for parsing and structuring EEG clinical reports.",
    "Harvard-EEG-Database-Tools": "Tools for managing and querying the Harvard EEG Database.",
    "Omega": "Data processing and analysis orchestration framework.",
    "Thunderpack": "High-performance data packaging format for large-scale EEG datasets.",
    "Thunderpack_WranglingCode": "Data wrangling utilities for Thunderpack-formatted datasets.",
    "Xltek_Annotation_Extraction": "Extraction of annotations from Xltek EEG recording systems.",
    "bdsp-boto3-example": "Example code for accessing BDSP data on AWS using boto3.",
    "bdsp-license-and-dua": "License templates and Data Use Agreements for BDSP datasets.",
    "bdsp-opendata-registry": "BDSP open data registry configuration and metadata.",
    "bdsp-reports-search-web-app": "Web application for searching BDSP clinical reports.",
    "bdsp.io_webapp_dev": "Development instance of the bdsp.io web application.",
    "bdsp.io_webapp_prod": "Production instance of the bdsp.io web application.",
    "bdsp_bidmc": "BDSP data integration tools for Beth Israel Deaconess Medical Center.",
    "cdac_google": "CDAC Google Cloud integration and automation scripts.",
    "dicom_deidentify": "De-identification pipeline for DICOM medical imaging files.",
    "medications_mgh": "MGH medication data extraction and analysis tools.",
    "mbw-zettelkasten": "Knowledge management and note-taking system for research.",
    "natus2json": "Converter for Natus EEG system files to JSON format.",
    "streaming_pipeline_code": "Real-time streaming data pipeline for continuous EEG monitoring.",
    "tensorizer": "Tools for converting EEG data into tensor formats for deep learning.",
    "plot-ecg": "Utility for plotting and visualizing ECG signal data.",
    "brandons-labyrinth": "Internal development and experimentation workspace.",
    "grant-banana": "Grant application management and tracking tools.",
    "YAMA": "Yet Another Management Application — internal project management tools.",
    "interrater_analysis": "Statistical tools for inter-rater agreement analysis.",
    "demo-repository": "Template repository demonstrating GitHub best practices for the org.",
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
    "Research Tools & Manuscript AI",
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


def _first_prose_paragraph(md):
    """Heuristic: from a Markdown blob, return the first plain-text paragraph
    that's neither a heading, badge, image, code block, nor HTML comment.
    Returns None if nothing prose-like was found."""
    if not md:
        return None
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    paragraph = []
    in_code = False
    skip_prefixes = ("#", ">", "<", "!", "```", "    ", "\t", "|", "---", "===")
    for ln in md.split("\n"):
        s = ln.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not s:
            if paragraph:
                break
            continue
        if any(s.startswith(p) for p in skip_prefixes):
            continue
        s = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", s)               # images
        s = re.sub(r"\[\]\([^)]+\)", "", s)                        # empty-text links (badge wrappers)
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)            # links
        s = re.sub(r"`([^`]+)`", r"\1", s)                         # inline code
        s = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", s)        # bold / italic
        s = s.strip()
        # require some actual letter content; otherwise it was badge / decoration noise
        if not s or len(re.sub(r"[^A-Za-z]", "", s)) < 8:
            continue
        paragraph.append(s)
        if len(" ".join(paragraph)) > 240:
            break
    if not paragraph:
        return None
    text = " ".join(paragraph).strip()
    if len(text) > 260:
        cut = max(text.rfind(". ", 0, 240), text.rfind("! ", 0, 240), text.rfind("? ", 0, 240))
        text = text[:cut + 1] if cut > 80 else text[:240].rsplit(" ", 1)[0] + "…"
    return text


def fetch_readme_description(name):
    """Fetch the repo's README and return its first prose paragraph (truncated),
    or None on any failure. Used as a fallback when neither the GitHub
    "About" nor REPO_DESCRIPTIONS has anything for a repo."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "bdsp-readme-fallback"}
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        req = Request(f"https://api.github.com/repos/{ORG_NAME}/{name}/readme", headers=headers)
        with urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        body = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
        return _first_prose_paragraph(body)
    except Exception:
        return None


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
        # Public + private repos are both listed. The catalog is treated as
        # org-member-first: private links work for members and 404 for others.
        # The visibility field is preserved in each entry so the rendered
        # card can show whether the repo is private (see _pages/code.md).
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

        description = (r.get("description")
                       or REPO_DESCRIPTIONS.get(name)
                       or fetch_readme_description(name)
                       or "No description provided.")
        repos.append({
            "name": name,
            "description": description,
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
