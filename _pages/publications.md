---
title: "CDAC - Publications"
layout: gridlay
excerpt: "CDAC - Publications."
sitemap: false
permalink: /publications/
---

# Publications
[**Higlighted publications**](#highlights)

**A full list of lab publications is available on [PubMed](https://www.ncbi.nlm.nih.gov/myncbi/m.%20brandon.westover.1/bibliography/public/) or [Google scholar](https://scholar.google.com/citations?hl=en&user=helCG6IAAAAJ).**

### By topic area   
**Critical care neurophysiology**  
[ICU EEG Terminology | ](#icu-eeg-terminology)
[Quantitative EEG / Spectrograms | ](#quantitative-eeg--spectrograms)
[Continuous EEG Monitoring| ](#continuous-eeg-monitoring)
[Seizure risk| ](#seizure-risk)
[Seizures| ](#seizures)
[Status epilepticus| ](#status-epilepticus)
[Ictal-interictal-injury continuum (IIIC)| ](#ictal-interictal-injury-continuum-iiic)
[Outcomes of seizures and IIIC| ](#outcomes-of-seizures-and-iiic)
[Triphasic waves| ](#triphasic-waves)
[Subarachnoid hemorrhage| ](#subarachnoid-hemorrhage)
[Epilepsy after acute brain injury| ](#epilepsy-after-acute-brain-injury)
[Delirium and encephalopathy| ](#delirium-and-encephalopathy)
[CAR-T cell therapy| ](#car-t-cell-therapy)
[Cardiac arrest and coma| ](#cardiac-arrest-and-coma)
[Burst suppression| ](#burst-suppression)
[Closed loop control](#closed-loop-control)

**Sleep**
[Sleep staging| ](#sleep-staging)
[Breathing| ](#breathing)
[Insomnia| ](#insomnia)
[Brain Age| ](#brain-age-index-bai)
[Spindles| ](#sleep-spindles)
[Dementia and sleep](#dementia-and-sleep)

**Epilepsy**
[Spike Detection| ](#spike-detection)
[Noise and bias| ](#noise-and-bias)
[Seizures| ](#seizures)
[Seizure forecasting| ](#seizure-forecasting)
[Epilepsy surgery| ](#epilepsy-surgery)
[Electroencephalography (EEG)| ](#electroencephalography-eeg)
[Epilepsy after acute brain injury](#epilepsy-after-acute-brain-injury)

**Brain Networks**
[Connectivity](#funcational-connectivity)

**Medical Decision Making**
[Decision analysis](#decision-analysis)

**Medical informatics**
[Non-neurology informatics| ](#non-neurology-informatics)
[Machine learning and AI| ](#machine-learning-and-ai)
[Risk prediction models| ](#risk-prediction-models)
[Electronic health records phenotyping & NLP| ](#electronic-health-records-phenotyping--nlp)
[Time series analysis| ](#time-series-analysis)
[COVID-19](#covid-19)

**Probability, statistics, information, causal inference**
[Probability, statistics, causal inference| ](#probability-statistics-causal-inference)
[Information theory](#information-theory)

**Sedation and anesthesia**
[Sedation and Anesthesia](#sedation-and-anesthesia)

**Computational Neuroscience**
[Computational neuroscience](#computational-neuroscience)

**General Neurology**
[General neurology](#general-neurology)

**Heart rate variability**
[Heart rate variability](#heart-rate-variability)

##  Highlights

{% assign number_printed = 0 %}
{% for publi in site.data.publist %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if publi.highlight == 1 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="col-sm-6 clearfix">
 <div class="well">
  <pubtit>{{ publi.title }}</pubtit>
  <img src="{{ site.url }}{{ site.baseurl }}/images/pubpic/{{ publi.image }}" class="img-responsive" width="33%" style="float: left" />
  <p>{{ publi.description }}</p>
  <p><em>{{ publi.authors }}</em></p>
  <p><strong><a href="{{ publi.link.url }}">{{ publi.link.display }}</a></strong></p>
  <p class="text-danger"><strong> {{ publi.news1 }}</strong></p>
  <p> {{ publi.news2 }}</p>
 </div>
</div>

{% assign number_printed = number_printed | plus: 1 %}

{% if even_odd == 1 %}
</div>
{% endif %}

{% endif %}
{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if even_odd == 1 %}
</div>
{% endif %}

<p> &nbsp; </p>

# Publications by topic
## Critical Care Neurophysiology
[Back to Top](#  )

### ICU EEG Terminology
[Back to Top](#  )
{% for publi in site.data.yamlICUEEGterminology %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Quantitative EEG / Spectrograms
[Back to Top](#  )
{% for publi in site.data.yamlQEEG %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Continuous EEG Monitoring
[Back to Top](#  )
{% for publi in site.data.yamlcEEG %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Seizure risk
[Back to Top](#  )
{% for publi in site.data.yamlszRisk %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Seizures
[Back to Top](#  )
{% for publi in site.data.yamlseizures %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Status epilepticus
[Back to Top](#  )
{% for publi in site.data.yamlstatusEpilepticus %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Ictal-interictal-injury continuum (IIIC)
[Back to Top](#  )
{% for publi in site.data.yamlszIIIC %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Outcomes of seizures and IIIC
[Back to Top](#  )
{% for publi in site.data.yamlszIIIC_harm %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Triphasic waves
[Back to Top](#  )
{% for publi in site.data.yamltpw %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Subarachnoid hemorrhage
[Back to Top](#  )
{% for publi in site.data.yamlSAH %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Epilepsy after acute brain injury
[Back to Top](#  )
{% for publi in site.data.yamlPTE %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Delirium and encephalopathy
[Back to Top](#  )
{% for publi in site.data.yamldelirium %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### CAR-T cell therapy
[Back to Top](#  )
{% for publi in site.data.yamlcarT %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Cardiac arrest and coma
[Back to Top](#  )
{% for publi in site.data.yamlcardiacArrest %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Burst suppression
[Back to Top](#  )
{% for publi in site.data.yamlburstSuppression %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Closed loop control
[Back to Top](#  )
{% for publi in site.data.yamlclosedLoopControl %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Sleep

[Back to Top](#  )

### Sleep staging
[Back to Top](#  )
{% for publi in site.data.yamlsleepStaging %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Breathing
[Back to Top](#  )
{% for publi in site.data.yamlbreathing %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Insomnia
[Back to Top](#  )
{% for publi in site.data.yamlinsomnia %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Brain Age Index (BAI)
[Back to Top](#  )
{% for publi in site.data.yamlbrainAge %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Sleep spindles
[Back to Top](#  )
{% for publi in site.data.yamlspindles %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Dementia and sleep
[Back to Top](#  )
{% for publi in site.data.yamldementia %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Epilepsy
### Spike Detection
[Back to Top](#  )
{% for publi in site.data.yamlspikeDetection %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Noise and bias
[Back to Top](#  )
{% for publi in site.data.yamlnoiseAndBias %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Seizures
[Back to Top](#  )
{% for publi in site.data.yamlseizures %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Seizure forecasting
[Back to Top](#  )
{% for publi in site.data.yamlszForecasting %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Epilepsy surgery
[Back to Top](#  )
{% for publi in site.data.yamlepilepsySurgery %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Electroencephalography (EEG)
[Back to Top](#  )
{% for publi in site.data.yamleeg %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Brain Networks
[Back to Top](#  )
### Funcational connectivity
[Back to Top](#  )
{% for publi in site.data.yamlconnectivity %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Computational neuroscience
[Back to Top](#  )
{% for publi in site.data.yamlcompNeuro %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Medical Decision Making
[Back to Top](#  )
### Decision analysis
[Back to Top](#  )
{% for publi in site.data.yamldecisionAnalysis %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Medical informatics
[Back to Top](#  )
### Non-neurology informatics
[Back to Top](#  )
{% for publi in site.data.yamlnon_neuro_informatics %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Machine learning and AI
[Back to Top](#  )
{% for publi in site.data.yamlML_AI %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Risk prediction models
[Back to Top](#  )
{% for publi in site.data.yamlriskPrediction %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Electronic health records phenotyping & NLP
[Back to Top](#  )
{% for publi in site.data.yamlehrPhenotyping %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Time series analysis
[Back to Top](#  )
{% for publi in site.data.yamltimeSeries %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### COVID-19
[Back to Top](#  )
{% for publi in site.data.yamlcovid %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Probability, statistics, information, causal inference
[Back to Top](#  )
### Probability, statistics, causal inference
[Back to Top](#  )
{% for publi in site.data.yamlprobStatsCausal %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

### Information theory
[Back to Top](#  )
{% for publi in site.data.yamlinfoTheory %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Sedation and anesthesia
[Back to Top](#  )
{% for publi in site.data.yamlsedationAndAnesthesia %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## General Neurology
[Back to Top](#  )
{% for publi in site.data.yamlgenNeuro %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )

## Heart rate variability
[Back to Top](#  )
{% for publi in site.data.yamlHRV_ECG %}
  {{ publi.title }} <br />
  <em>{{ publi.authors }} </em><br /><a href="{{ publi.link.url }}">{{ publi.link.display }}</a>
{% endfor %}
[Back to Top](#  )