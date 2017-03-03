# web-monitoring

The repository is for documentation and managing project-wide issues.

## Project Goals

See [this page on the EDGI website](https://envirodatagov.org/version-tracking/).
For more detail on how web monitoring is currently being done, watch this
[50-minute training video](https://www.dropbox.com/s/ciixvu612ktf4nt/new_tracking_training.mp4?dl=0). The project aims to develop a more sophisticated and automated
system for accomplishing the same task.

## Architecture of the web-monitoring project

The project is current divided into three repositories handling complementary
aspects of the task. They can be developed and upgraded semi-independently,
communicating via agreed-upon interfaces.

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
