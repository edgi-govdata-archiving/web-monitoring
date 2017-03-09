# Web Monitoring

This repository is for EDGI [Web Monitoring Project](https://github.com/edgi-govdata-archiving/web-monitoring) documentation and project-wide issue management.

EDGI is already monitoring tens of thousands of pages and will eventually be monitoring tens of millions (or even as many as ~1 billion). Currently there is a lot of manual labour that goes into reviewing all changes, regardless of whether they are meaningful or not. Any system will need to emphasize usability of the UI and efficiency of computational resources.

## Project Goals

The purpose of the system is to enable analysts to quickly review monitored government websites in order to report on [__meaningful changes__](#identifying-meaningful-changes). The Website Monitoring automated system aims to make these changes easy to track, review, and report on.

For more, see [the Version Tracking page on the EDGI website](https://envirodatagov.org/version-tracking/) and watch this
[50-minute Analyst training video](https://www.dropbox.com/s/ciixvu612ktf4nt/new_tracking_training.mp4?dl=0).

## Specification

In order to be useful, tools will need to be able to do the following:

1. read archive directories and identify comparison candidates for a given URL
2. perform diffs on large numbers of pages (a useful scale for our work is the "subdomain" -- a full or partial government domain that we have identified as relevant to environment/climate change)
3. filter those diffs to eliminate irrelevant, trivial, or repetitive changes
4. output results in a form that is immediately acessible/helpful to an analyst. One likely format is a CSV file containing at least the following information:
   - page title
   - page url
   - comparison dates
   - **link to user-friendly diff** -- this can be local or served over http

## Architecture

The project is current divided into three repositories handling complementary aspects of the task. They can be developed and upgraded semi-independently, communicating via agreed-upon interfaces:
* [**web-monitoring-db**](https://github.com/edgi-govdata-archiving/web-monitoring-db)  
  A Ruby on Rails app for serves diffs from a database and collects
  human-entered annotations.
* [**web-monitoring-ui**](https://github.com/edgi-govdata-archiving/web-monitoring-ui)  
  Front-end code (in TypeScript) provides useful views of the diffs. It
  communicates with the Rails app via JSON.
* [**web-monitoring-processing**](https://github.com/edgi-govdata-archiving/web-monitoring-processing)  
  A Python backend ingests new captured HTML, computes diffs (for now, by
  querying PageFreezer), performs prioritization/filtering, and populates
  databases for Rails app.

## Resources

### Identifying "Meaningful Changes"

The vast majority of changes to web pages are not relevant to analysts and we want to avoid presenting those irrelevant changes to analysts at all. It is, of course, not trivial to identify "meaningful" changes immediately, and we expect that analysts will always be involved in a decision about whether some changes are "important" or not. However, as we expand from 10<sup>4</sup> to 10<sup>7</sup> webpages, we need to drastically reduce the number of pages that analysts look at. 

Some examples of **meaningless** changes: 
- it's not unusual for a page to have a view counter on the bottom. In this case, the page changes **by definition** every time you view it.
- many sites have "content sliders" or news feeds that update periodically. This change may be "meaningful", in that it's interesting to see news updates. But it's only interesting once, not (as is sometimes seen) 1000 or 10000 times.

An example of a **meaningful** change: 
- In February, we noticed a systematic replacement of the word "impact" with the word "effect" on one website. This change is very interesting because while "impact" and "effect" have similar meanings, "impact" is a **stronger** word. So there is an effort being made to **weaken** the language on existing sites. Our question is in part: what tools would we need in order to have this change **flagged** by our tools and presented to the analyst as **potentially interesting**?

### Sample Data

[`example-data`](./example-data) contains examples of website changes:

- `falsepos-...` files are cases any filter should catch
- `truepos...` files are cases of changes we care about

Filters will need to be tested (and possibly trained) against real datasets at some point
