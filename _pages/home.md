---
title: "CDAC - The Westover Lab at Stanford"
layout: homelay
excerpt: "CDAC, the Westover Lab at Stanford: AI methods for EEG, sleep recordings and clinical records, with the data and tools shared for other researchers."
sitemap: false
permalink: /
---

<div class="rd" markdown="0">

  <div class="rd-stack">
    {% include preview-note.html title="Identity." text="The name now carries a plain descriptor, and the menu has five destinations. Values, Resources, Pictures, Fun, News and EEGTalk are in the footer; nothing is removed." %}
    <div class="rd-hero">
      <div class="rd-stack">
        <p class="rd-label">Clinical Data Animation Center &middot; Stanford Medicine</p>
        <h1>Making brain data useful for neurological care</h1>
        <p class="rd-lede">We develop and validate AI methods for EEG, sleep recordings and clinical records, to improve how neurological disease is measured, predicted and treated. We release the data and tools behind this work so other researchers can use them.</p>
        <p>Led by <a href="{{ site.url }}{{ site.baseurl }}/brandon/">M. Brandon Westover, MD, PhD</a>, CDAC brings together clinicians, scientists and engineers at Stanford and collaborating institutions.</p>
        <div class="rd-routes">
          <a class="rd-btn is-primary" href="{{ site.url }}{{ site.baseurl }}/research/">Explore our research</a>
          <a class="rd-btn" href="{{ site.url }}{{ site.baseurl }}/code">Find data and software</a>
          <a class="rd-btn" href="{{ site.url }}{{ site.baseurl }}/openings">Join the team</a>
        </div>
      </div>
      <figure class="rd-figure">
        <div class="rd-mat"><img src="{{ site.url }}{{ site.baseurl }}/images/home/sleep-spectrograms.jpg" alt="Two overnight sleep EEG spectrograms with sleep-stage plots above them. The first, from a 58-year-old man, is labelled high risk; the second, from a 61-year-old man, is labelled low risk."></div>
        <figcaption><strong>Two nights of sleep, as a model reads them.</strong> Each panel shows one person's sleep stages (top) and the frequency content of their EEG through the night (bottom). A model trained on sleep recordings placed the first night at the 95th percentile of predicted mortality risk and the second at the 5th. <a href="{{ site.url }}{{ site.baseurl }}/research/">What sleep reveals about brain health</a></figcaption>
      </figure>
    </div>
    {% include preview-note.html title="Hero." text="The heading says what the group does, and one explained figure replaces the 17-image carousel (those images are still on the Pictures page). Please confirm the caption." %}
  </div>

  <div class="rd-stack">
    <h2>Who we are</h2>
    <dl class="rd-identity">
      <dt>The group</dt>
      <dd>The Clinical Data Animation Center (CDAC), the research group of M. Brandon Westover.</dd>
      <dt>Based at</dt>
      <dd>Department of Neurology and Neurological Sciences, Stanford University School of Medicine.</dd>
      <dt>Led by</dt>
      <dd>M. Brandon Westover, MD, PhD, Director of the Stanford Epilepsy Center and of the Neurologic Artificial Intelligence Center.</dd>
      <dt>Platform</dt>
      <dd>CDAC runs the <a href="https://bdsp.io/">Brain Data Science Platform (BDSP)</a>, which shares clinical EEG, sleep and related datasets with researchers.</dd>
      <dt>People</dt>
      <dd><a href="{{ site.url }}{{ site.baseurl }}/team">The team, affiliated investigators and collaborators</a></dd>
    </dl>
    {% include preview-note.html title="Needs your wording." text="Two lines are left out until you supply them: one sentence on how the Neurologic AI Center relates to CDAC, and the list of collaborating institutions you want named here." %}
  </div>

  <div class="rd-stack">
    <h2>What we have built</h2>
    <p class="rd-measure rd-muted">Four examples, each with the evidence behind it. The full record is on the <a href="{{ site.url }}{{ site.baseurl }}/publications">publications page</a>.</p>
    <div class="rd-grid2">
      <div class="rd-item">
        <p class="rd-label">EEG interpretation</p>
        <h3>A foundation model for reading clinical EEG</h3>
        <p>MORGOTH was developed and validated across multiple centres to interpret EEG automatically and comprehensively.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/42642264/">Lancet Digital Health, 2026</a><a href="https://github.com/bdsp-core/morgoth">Code</a></p>
      </div>
      <div class="rd-item">
        <p class="rd-label">Sleep and brain health</p>
        <h3>Measures of brain health from a night of sleep</h3>
        <p>Sleep EEG yields a brain age and a brain health score that track cognition and long-term outcomes.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/42769852/">Sleep Advances, 2026</a><a href="https://github.com/bdsp-core/SleepEEGBasedBrainAge">Code</a></p>
      </div>
      <div class="rd-item">
        <p class="rd-label">Critical care</p>
        <h3>EEG patterns and recovery after cardiac arrest</h3>
        <p>A multicentre study of 1,000 patients in coma after cardiac arrest, alongside the I-CARE EEG database that we share with other researchers.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/42677185/">Neurology Open Access, 2026</a><a href="https://bdsp.io/content/bdsp-icare/2.0/">I-CARE data</a></p>
      </div>
      <div class="rd-item">
        <p class="rd-label">Shared data</p>
        <h3>Clinical sleep recordings across the human lifespan</h3>
        <p>The Human Sleep Project is a multi-centre polysomnography dataset, released through BDSP for other groups to build on.</p>
        <p class="rd-links"><a href="https://pubmed.ncbi.nlm.nih.gov/42555111/">Sleep, 2026</a><a href="https://bdsp.io/">Data on BDSP</a></p>
      </div>
    </div>
    {% include preview-note.html title="Your pick." text="I chose these four from recent papers. Swap in the four that best represent the program; each needs a one-line description and its links." %}
  </div>

  <div class="rd-stack">
    <h2>Latest</h2>
    {% include news-list.html limit=6 %}
    <p><a href="{{ site.url }}{{ site.baseurl }}/allnews.html">All news</a></p>
    {% include preview-note.html title="News." text="Same automatic feed as before. The only addition is the label (Paper, Preprint, Data &amp; code, News), worked out from where each item was published." %}
  </div>

</div>
