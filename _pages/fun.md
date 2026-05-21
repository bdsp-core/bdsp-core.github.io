---
title: "CDAC - Fun"
layout: textlay
excerpt: "Fun and useful interactive tools from the CDAC lab."
sitemap: false
permalink: /fun/
---

# Fun

A small collection of interactive tools, demos, and learning aids built by the lab. Most run entirely in your browser — nothing to install.

### Dynamotype onset/offset trainer
A quiz tool to help you learn to recognize seizure **dynamotypes** — the characteristic onset and offset patterns of seizures. It drills you on the dynamotype taxonomy from Stacey and colleagues' "Dynamotypes for Dummies" toolbox and atlas.

[**Launch the dynamotype trainer →**]({{ site.url }}{{ site.baseurl }}/fun/dynamotype_quiz.html)

<small>Based on: Sheckler C, Kish K, Walker Z, Barkelew G, Crisp DN, Szuromi MP, Saggio ML, Stacey WC. *Dynamotypes for Dummies: A Toolbox, Atlas, and Tutorial for Simulating a Comprehensive Range of Realistic Synthetic Seizures.* eNeuro. 2025 Oct 23;12(10):ENEURO.0200-25.2025. doi: [10.1523/ENEURO.0200-25.2025](https://doi.org/10.1523/ENEURO.0200-25.2025). PMID: [41027733](https://pubmed.ncbi.nlm.nih.gov/41027733/); PMCID: PMC12549069. Code: [Dynamotypes-for-Dummies](https://github.com/Dynamotypes-for-Dummies).</small>

### Seizure bifurcations: onset & offset phase portraits
Seizures begin and end through distinct dynamical mechanisms, and a landmark idea in computational epilepsy — the Saggio–Jirsa taxonomy of seizure "dynamotypes" — classifies them by the type of bifurcation that switches the brain between resting and oscillating states. There are four ways a seizure can start and four ways it can stop, and each leaves a characteristic fingerprint in the EEG: a sudden jump, a gradual ramp-up in frequency or amplitude, a slowing-down before it stops, and so on.

This tool lets you see why. For each onset and offset type, the left panel shows the **phase portrait** — the geometry of the system's possible states, with its fixed points, limit cycles, and flow — while the panel below shows the resulting voltage trace *x(t)*. As the controlling parameter sweeps through its critical value, you watch the state space reorganize and the signal's signature emerge in lockstep. The bright marker is the system's current state; its position is projected onto the voltage axis so you can connect "where the system is" to "what the EEG shows."

**How to use it:** Toggle between Onset and Offset, then either press Play or drag the timeline handle to scrub through the transition. Slow it down to study the slow regions. Click a single type to see its vector field and labeled equilibria up close, or turn on the Flow swarm to watch how a whole cloud of starting states flows through the bifurcation.

[**Launch the bifurcation animator →**]({{ site.url }}{{ site.baseurl }}/fun/onset_offset_anim.html)

<small>Based on: Sheckler C, Kish K, Walker Z, Barkelew G, Crisp DN, Szuromi MP, Saggio ML, Stacey WC. *Dynamotypes for Dummies: A Toolbox, Atlas, and Tutorial for Simulating a Comprehensive Range of Realistic Synthetic Seizures.* eNeuro. 2025 Oct 23;12(10):ENEURO.0200-25.2025. doi: [10.1523/ENEURO.0200-25.2025](https://doi.org/10.1523/ENEURO.0200-25.2025). PMID: [41027733](https://pubmed.ncbi.nlm.nih.gov/41027733/); PMCID: PMC12549069. Code: [Dynamotypes-for-Dummies](https://github.com/Dynamotypes-for-Dummies).</small>
