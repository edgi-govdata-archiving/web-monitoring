# Web Monitoring

This repository is for EDGI [Web Monitoring Project](https://github.com/edgi-govdata-archiving/web-monitoring) documentation and project-wide issue management.

EDGI is already monitoring tens of thousands of pages and will eventually be monitoring tens of millions (or even as many as ~1 billion). Currently there is a lot of manual labour that goes into reviewing all changes, regardless of whether they are meaningful or not. Any system will need to emphasize usability of the UI and efficiency of computational resources.

## Project Goals

The purpose of the system is to enable analysts to quickly review monitored government websites in order to report on __meaningful changes__. The Website Monitoring automated system aims to make these changes easy to track, review, and report on.

For more, see [the Version Tracking page on the EDGI website](https://envirodatagov.org/version-tracking/) and watch this
[50-minute Analyst training video](https://www.dropbox.com/s/ciixvu612ktf4nt/new_tracking_training.mp4?dl=0).

## Project Architecture

The project is current divided into three repositories handling complementary aspects of the task. They can be developed and upgraded semi-independently, communicating via agreed-upon interfaces.

* [web-monitoring-db](https://github.com/edgi-govdata-archiving/web-monitoring-db)
  -- A Ruby on Rails app for serves diffs from a database and collects
  human-entered annotations.

* [web-monitoring-ui](https://github.com/edgi-govdata-archiving/web-monitoring-ui)
  -- Front-end code (in TypeScript) provides useful views of the diffs. It
  communicates with the Rails app via JSON.

* [web-monitoring-backend](https://github.com/edgi-govdata-archiving/web-monitoring-backend)
  -- A Python backend ingests new captured HTML, computes diffs (for now, by
  querying PageFreezer), performs prioritization/filtering, and populates
  databases for Rails app.
