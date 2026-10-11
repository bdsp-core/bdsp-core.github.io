---
title: "CDAC - Team"
layout: gridlay
excerpt: "CDAC: Team members"
sitemap: false
permalink: /team/
---

<!-- Updated: May 29, 2025 - CSS-based image standardization -->
# People

{% include preview-note.html title="Regrouped, same people." text="The five lists are unchanged and still sync from the team spreadsheet. They are regrouped: the group as it is today comes first (Engineering plus Postdocs, Students, Staff), then the faculty who lead projects with it, then collaborators and alumni. Brandon is the first Faculty row. If someone sits in the wrong group, move their row in the spreadsheet." %}

**We are looking for postdocs, engineers and students to join the team** [(see how to join)]({{ site.url }}{{ site.baseurl }}/openings)**.**

Jump to [Principal investigator](#principal-investigator), [Core team](#core-team), [Affiliated investigators](#affiliated-investigators), [Collaborators](#collaborators), [Alumni](#alumni).

## Principal investigator
{% assign pi = site.data.faculty | slice: 0, 1 %}
{% include team-grid.html members=pi %}

## Core team
The group as it is today: engineers, postdocs, students and staff.
{: .rd-muted}

{% assign core = site.data.engineering | concat: site.data.postdocsStudentsStaff %}
{% include team-grid.html members=core %}

## Affiliated investigators
Faculty who lead projects with the group.
{: .rd-muted}

{% assign affiliated = site.data.faculty | slice: 1, 500 %}
{% include team-grid.html members=affiliated %}

## Collaborators
{% include team-grid.html members=site.data.collaborators %}

## Alumni
{% include team-grid.html members=site.data.alumni %}
