[![Code of Conduct](https://img.shields.io/badge/%E2%9D%A4-code%20of%20conduct-blue.svg?style=flat)](https://github.com/edgi-govdata-archiving/overview/blob/master/CONDUCT.md) &nbsp;[![Project Status Board](https://img.shields.io/badge/✔-Project%20Status%20Board-green.svg?style=flat)](https://github.com/orgs/edgi-govdata-archiving/projects/4)

# EDGI: Web Monitoring Project

[**Website Monitoring**][webmon] is an [EDGI][edgi] project building tools and community around monitoring changes to government websites, both environment-related and otherwise. It includes technical tools for:

- Loading, storing, and analyzing historical snapshots of web pages
- Providing an API for retrieving and updating data about those snapshots
- A website for visualizing and browsing changes between those snapshots
- Tools for managing the workflow of a team of human analysts using the above tools to track and publicize information about meaningful changes to government websites.

EDGI uses these tools to publish reports that are written about in major publications such as [The Atlantic][article_energykids] or [Vice][article_termanalysis]. Teams at other organizations use parts of this project for similar purposes or to provide comparisons between different versions of public web pages.

This project and its associated efforts are already monitoring tens of thousands of government web pages. But we aspire for larger impact, eventually monitoring tens of millions or more. Currently, there is a lot of manual labor that goes into reviewing all changes, regardless of whether they are meaningful or not. Any system will need to emphasize usability of the UI and efficiency of computational resources.

**For a combined view of all issues and status, check [the project board][project_board].** This [repository][repo] is for project-wide documentation and [issues][issues].

  [edgi]: https://envirodatagov.org/
  [webmon]: https://envirodatagov.org/website-monitoring/ 
  [article_energykids]: https://www.theatlantic.com/science/archive/2017/02/energy-kids/516978/
  [article_termanalysis]: https://www.vice.com/en_ca/article/kzmmwe/under-trump-26-of-climate-change-references-have-vanished-from-gov-sites
  [repo]: https://github.com/edgi-govdata-archiving/web-monitoring
  [issues]: https://github.com/edgi-govdata-archiving/web-monitoring/issues
  [project_board]: https://github.com/orgs/edgi-govdata-archiving/projects/4

- [Project Structure](#project-structure)
- [Get Involved](#get-involved)
- [Project Overview](#project-overview)
- [Code of Conduct](#code-of-conduct)
- [Contributors & Sponsors](#contributors)
- [License & Copyright](#license--copyright)

## Project Structure

The technical tooling for Web Monitoring is broken up into several repositories, each named `web-monitoring-{name}`:

| Repo | Description | Tools Used |
| ---- | ----------- | ---------- |
| [web-monitoring](https://github.com/edgi-govdata-archiving/web-monitoring) | **(This Repo!)** Project-wide documentation and issue tracking. | Markdown |
| [web-monitoring-db](https://github.com/edgi-govdata-archiving/web-monitoring-db) | A database and API that stores metadata about the pages, versions, changes we track, as well as human annotations about those changes. | Ruby, Rails, Postgresql |
| [web-monitoring-ui](https://github.com/edgi-govdata-archiving/web-monitoring-ui) | A web-based UI (built in React) that shows diffs between different versions of the pages we track. It’s built on the API provided by web-monitoring-db. | JavaScript, React |
| [web-monitoring-processing](https://github.com/edgi-govdata-archiving/web-monitoring-processing) | A suite of Python tools for diffing web pages in a variety of ways and for interfacing with external services like [the Internet Archive](https://archive.org). | Python, Tornado |
| [web-monitoring-versionista-scraper](https://github.com/edgi-govdata-archiving/web-monitoring-versionista-scraper) | A set of Node.js scripts that extract data from Versionista and load it into web-monitoring-db. It also generates the CSV files that analysts currently use to manage their work on a weekly basis. | Node.js |
| [web-monitoring-ops](https://github.com/edgi-govdata-archiving/web-monitoring-ops) | Server configuration and other deployment information for managing EDGI’s live instance of all these tools. | Kubernetes, Bash, AWS |

For more on how all these parts fit together, see [ARCHITECTURE.md](https://github.com/edgi-govdata-archiving/web-monitoring/blob/master/ARCHITECTURE.md).

## Get Involved

We’d love your help on improving this project! If you are interested in getting involved…

* Chat with us on [Slack (https://archivers.slack.com)](https://archivers.slack.com)
    * You can sign up for an account at https://archivers-slack.herokuapp.com/
    * Join us in the `#webmonitoring` channel.
* Please follow EDGI's [Code of Conduct](https://github.com/edgi-govdata-archiving/overview/blob/master/CONDUCT.md)

This project is two-part! We rely both on **open source code contributors** (building this tool) and on **volunteer analysts** who use the tool to identify and characterize changes to government websites.

### Get involved as an analyst
* Read through the [Project Overview](#project-overview) and especially the section on "meaningful changes" to get a better idea of the work
* Contact us either over Slack or at edgi.websitemonitoring@protonmail.com to ask for a quick training

### Get involved as a programmer
* Be sure to check our [contributor guidelines](https://github.com/edgi-govdata-archiving/web-monitoring/blob/master/CONTRIBUTING.md)
* Take a look through the repos listed in the [Project Structure](#project-structure) section and choose one that feels appropriate to your interests and skillset
* Try to get the repo running on your machine (and if you have any challenges, please make issues about them!)
* Find an issue labeled `good-first-issue` and work to resolve it

## Project Overview

### Project Goals

The purpose of the system is to enable analysts to quickly review monitored government websites in order to report on [__meaningful changes__](#identifying-meaningful-changes). In order to do so, the system, a.k.a. Scanner, does several major tasks:

1. Interfaces with other archival services (like the Internet Archive) to _save snapshots of web pages_.
2. _Imports_ those snapshots and other metadata from archival sources.
3. Determines _which snapshots represent a change_ from a previous version of the page.
4. Process changes to automatically _determine a priority_ or _sift out meaningful changes_ for deeper analysis by humans.
5. Volunteers and experts work together to _further sift out meaningful changes_ and qualify them for journalists by writing reports.
4. Journalists _build narratives and amplify stories_ for the wider public.


### Identifying "Meaningful Changes"

The majority of changes to web pages are not relevant and we want to avoid presenting those irrelevant changes to human analysts. Identifying irrelevant changes in an automated way is not easy, and we expect that analysts will always be involved in a decision about whether some changes are "important" or not.

However, as we expand the number of web pages we monitor, we definitely need to develop tools to reduce the number of pages that analysts must look at. 

Some examples of **meaningless** changes: 
- it's not unusual for a page to have a view counter on the bottom. In this case, the page changes **by definition** every time you view it.
- many sites have "content sliders" or news feeds that update periodically. This change may be "meaningful", in that it's interesting to see news updates. But it's only interesting once, not (as is sometimes seen) 1000 or 10000 times.

An example of a **meaningful** change: 
- In February, we noticed a systematic replacement of the word "impact" with the word "effect" on one website. This change is very interesting because while "impact" and "effect" have similar meanings, "impact" is a **stronger** word. So, there is an effort being made to **weaken** the language on existing sites. Our question is in part: what tools would we need in order to have this change **flagged** by our tools and presented to the analyst as **potentially interesting**?

### Sample Data

The [`example-data`](./example-data) folder contains examples of website changes to use for analysis.


## Code of Conduct

This repository falls under EDGI's [Code of Conduct](https://github.com/edgi-govdata-archiving/overview/blob/master/CONDUCT.md).


## Contributors

### Individuals

This project wouldn’t exist without a lot of amazing people’s help. Thanks to the following for their work reviewing URL's, monitoring changes, writing [reports](https://envirodatagov.org/website-monitoring/), and a slew of so many other things!

<!-- ALL-CONTRIBUTORS-LIST:START -->
| Contributions | Name |
| ----: | :---- |
| [🔢](# "Content") | Chris Amoss |
| [🔢](# "Content") [📋](# "Organizer") [🤔](# "Ideas and Planning") | Maya Anjur-Dietrich |
| [🔢](# "Content") | Marcy Beck |
| [🔢](# "Content") [📋](# "Organizer") [🤔](# "Ideas and Planning") | Andrew Bergman |
| [📖](# "Documentation") | Kelsey Breseman |
| [🔢](# "Content") | Madelaine Britt |
| [🔢](# "Content") | Ed Byrne |
| [🔢](# "Content") | Morgan Currie |
| [🔢](# "Content") | Justin Derry |
| [🔢](# "Content") [📋](# "Organizer") [🤔](# "Ideas and Planning") | Gretchen Gehrke |
| [🔢](# "Content") | Jon Gobeil |
| [🔢](# "Content") | Pamela Jao |
| [🔢](# "Content") | Sara Johns |
| [🔢](# "Content") | Abby Klionski |
| [🔢](# "Content") | Katherine Kulik|
| [🔢](# "Content") | Aaron Lamelin |
| [🔢](# "Content") [📋](# "Organizer") [🤔](# "Ideas and Planning") | Rebecca Lave |
| [🔢](# "Content") | Eric Nost |
| [📖](# "Documentation") | Karna Patel |
| [🔢](# "Content") | Lindsay Poirier |
| [🔢](# "Content") [📋](# "Organizer") [🤔](# "Ideas and Planning") | Toly Rinberg|
| [🔢](# "Content") | Justin Schell |
| [🔢](# "Content") | Lauren Scott |
| [🤔](# "Ideas and Planning") [🔍](# "Funding/Grant Finders")| Nick Shapiro |
| [🔢](# "Content") | Miranda Sinnott-Armstrong |
| [🔢](# "Content") | Julia Upfal |
| [🔢](# "Content") | Tyler Wedrosky |
| [🔢](# "Content") | Adam Wizon |
| [🔢](# "Content") | Jacob Wylie |

<!-- ALL-CONTRIBUTORS-LIST:END -->

(For a key to the contribution emoji or more info on this format, check out [“All Contributors.”](https://github.com/kentcdodds/all-contributors))


### Sponsors & Partners

Finally, we want to give a huge thanks to partner organizations that have helped to support this project with their tools and services:

- [The David and Lucile Packard Foundation](https://www.packard.org)
- [Doris Duke Charitable Foundation](http://www.ddcf.org)
- [Amazon Web Services](https://aws.amazon.com/)
- [Sentry.io](https://sentry.io)
- [PageFreezer](https://www.pagefreezer.com)
- [Google Cloud Platform](https://cloud.google.com)
- [Google Summer of Code](https://summerofcode.withgoogle.com)
- [DataKind](http://www.datakind.org/)
- [The Internet Archive](https://archive.org/)


## License & Copyright

Copyright (C) 2017-2019 Environmental Data and Governance Initiative (EDGI) <br /> <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" /></a> Web Monitoring documentation in this repository is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>. See the [`LICENSE`](https://github.com/edgi-govdata-archiving/web-monitoring/blob/master/LICENSE) file for details.

Software code in other Web Monitoring repositories is generally licensed under the GPL v3 license, but make sure to check each repository’s README for specifics.

