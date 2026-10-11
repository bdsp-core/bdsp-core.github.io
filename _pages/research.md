---
title: "CDAC - Research"
layout: textlay
excerpt: "Four questions the Westover Lab works on: reliable EEG interpretation, sleep and brain health, brain monitoring in critical illness, and shared data for neurological research."
sitemap: false
permalink: /research/
---

<div class="rd" markdown="0">

  <div class="rd-stack">
    <p class="rd-label">Research</p>
    <h1>Four questions we work on</h1>
    <p class="rd-lede rd-measure">A short introduction to the program. For a specific paper, see <a href="{{ site.url }}{{ site.baseurl }}/publications">all publications, by topic</a>.</p>
    {% include preview-note.html title="New page." text="This replaces the template text that is live at /research/ today. Each project gives the problem, what the group did, and links. A sentence on the main result and its limits would strengthen each one; I have left those for you and the lead authors rather than guess." %}
  </div>

  <div class="rd-question">
    <h2>Can EEG interpretation be made more reliable and scalable?</h2>
    <div class="rd-projects">
      <div class="rd-project">
        <h3>MORGOTH, an EEG foundation model</h3>
        <p>Reading EEG takes scarce expert time. MORGOTH is a single model for comprehensive automated interpretation, developed and validated at multiple centres.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/42642264/">Lancet Digital Health, 2026</a><a href="https://github.com/bdsp-core/morgoth">Code</a></p>
      </div>
      <div class="rd-project">
        <h3>How much do experts agree?</h3>
        <p>We measured interrater reliability among expert electroencephalographers identifying seizures and rhythmic and periodic patterns, and the noise in expert diagnosis of epilepsy.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/36460472/">Neurology, 2023</a><a href="https://pubmed.ncbi.nlm.nih.gov/41556879/">Epileptic Disorders, 2026</a><a href="https://github.com/bdsp-core/IIIC-IRR">Code</a></p>
      </div>
      <div class="rd-project">
        <h3>Detecting epileptiform spikes</h3>
        <p>SpikeNet is a deep learning model for automated detection of interictal epileptiform discharges in EEG.</p>
        <p class="rd-links"><a href="https://github.com/bdsp-core/SpikeNet2">Code</a></p>
      </div>
    </div>
  </div>

  <div class="rd-question">
    <h2>What does sleep reveal about brain health?</h2>
    <div class="rd-projects">
      <div class="rd-project">
        <h3>Brain age and brain health from sleep EEG</h3>
        <p>A brain age estimated from one night's EEG, and a sleep-derived brain health score studied against long-term cognitive decline.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/42769852/">Sleep Advances, 2026</a><a href="https://github.com/bdsp-core/SleepEEGBasedBrainAge">Code</a></p>
      </div>
      <div class="rd-project">
        <h3>Breathing instability during sleep</h3>
        <p>Dynamic instability of breathing during sleep, quantified from routine recordings, predicts cognition, disease and mortality.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/42536396/">Sleep, 2026</a></p>
      </div>
      <div class="rd-project">
        <h3>CAISR, the Complete AI Sleep Report</h3>
        <p>Automated scoring of clinical sleep studies, so that large sleep datasets can be analysed consistently.</p>
        <p class="rd-links"><a href="https://github.com/bdsp-core/CAISR-App">Software</a></p>
      </div>
    </div>
  </div>

  <div class="rd-question">
    <h2>How should brain monitoring inform care in critical illness?</h2>
    <div class="rd-projects">
      <div class="rd-project">
        <h3>Coma after cardiac arrest</h3>
        <p>EEG patterns and their prognostic significance in a multicentre cohort of 1,000 patients, and an international EEG database for outcome prediction research.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/42677185/">Neurology Open Access, 2026</a><a href="https://bdsp.io/content/bdsp-icare/2.0/">I-CARE data</a></p>
      </div>
      <div class="rd-project">
        <h3>Seizures and the ictal-interictal continuum</h3>
        <p>SPaRCNet classifies seizures and rhythmic and periodic patterns in ICU EEG; GROND describes those patterns quantitatively.</p>
        <p class="rd-links"><a href="https://github.com/bdsp-core/IIIC-SPaRCNet">SPaRCNet</a><a href="https://bdsp.io/content/s58yrgqds7xqn8622x7u/1.0.0/">GROND</a></p>
      </div>
    </div>
  </div>

  <div class="rd-question">
    <h2>How can shared data and clinical records speed up neurological research?</h2>
    <div class="rd-projects">
      <div class="rd-project">
        <h3>Brain Data Science Platform</h3>
        <p>Clinical EEG, sleep and ECG datasets released for reuse, including the Human Sleep Project and the Harvard-Emory ECG Database.</p>
        <p class="rd-links"><a href="https://bdsp.io/">bdsp.io</a><a href="https://pubmed.ncbi.nlm.nih.gov/42555111/">Sleep, 2026</a><a href="https://pubmed.ncbi.nlm.nih.gov/41741499/">Scientific Data, 2026</a></p>
      </div>
      <div class="rd-project">
        <h3>Phenotypes from the medical record</h3>
        <p>Methods that extract diagnoses and outcomes from clinical notes, such as cognitive impairment and functional outcome after cardiac arrest.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/40222334/">Int J Med Inform, 2025</a><a href="https://pubmed.ncbi.nlm.nih.gov/42806261/">Neurocritical Care, 2026</a></p>
      </div>
    </div>
  </div>

</div>
