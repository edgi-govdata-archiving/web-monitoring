# EDGI: Web Monitoring Project

[**Environmental Data & Governance Initiative**][edgi] (EDGI) is an
international network of academics and non-profits addressing potential
threats to federal environmental and energy policy, and to the
scientific research infrastructure built to investigate, inform, and
enforce them.

[**Website Monitoring**][webmon] is an EDGI project aspiring to build
tools and community around monitoring changes to government websites,
both environment-related and otherwise.

   [edgi]: https://envirodatagov.org/
   [webmon]: https://envirodatagov.org/website-monitoring/ 

This [repository][repo] is for project-wide documentation and [issues-tracking][issues].

   [repo]: https://github.com/edgi-govdata-archiving/web-monitoring
   [issues]: https://github.com/edgi-govdata-archiving/web-monitoring/issues

This project and its associated efforts are already monitoring tens of thousands of government web pages.
But we aspire for larger impact, eventually monitoring tens of millions or more.
Currently, there is a lot of manual labor that goes into reviewing all changes,
regardless of whether they are meaningful or not.
Any system will need to emphasize usability of the UI and efficiency of computational resources.

- [Technologies Used](#hammer-technologies-used)
- [Project Goals](#project-goals)
- [How to Help](#how-to-help)
- [Project Overview](#project-overview)
- [License & Copyright](#license--copyright)

You can **track upcoming releases** by exploring our [milestones](https://github.com/edgi-govdata-archiving/web-monitoring/milestones).

## :hammer: Technologies Used

To help newcomers better understand where they might be able to
contribute, these are the main tools that we use and are having
discussions around within this project. This includes software in
the application, but also platforms that we rely on.

And don't worry -- you definitely don't need to know all of them!

* **HTML & CSS.**
* **SASS.**
* [**Ruby on Rails.**][rails] A web application development framework used for API server.
* **Javascript.** Notable packages include:
    * [**Webpack.**][webpack] A _static module bundler_ for modern JavaScript
      applications.
    * [**ReactJS.**][reactjs] A JavaScript library for building user
      interfaces.
* **Python.** Notable packages include:
    * [**Beautiful Soup.**][beautifulsoup] A library for pulling data out
      of HTML and XML files.
    * [**Tornado.**][tornado] A web server and application framework.
* [**Postgresql.**][postgres] A powerful, open source
  object-relational database system.
* [**Redis.**][redis] An open source, in-memory data structure store,
  used as a database, cache and message broker.
* [**Swagger.**][swagger] A spec and framework for API developer tools.
* [**Heroku.**][heroku] A platform for easily deploying applications.
* [**Ansible.**][ansible] An open source automation platform for
  software configuration.
* [**Docker.**][docker] Runs "containers images" to help make running
  software simpler for developers.
* [**Versionista.**][versionista] Enterprise tool for webpage change
  detection and alerts.
* [**Internet Archive.**][ia] A nonprofit-led digital library of
  Internet website history going back 20+ years.
* [**Amazon Web Services. (AWS)**][aws] A hosted cloud services platform
  for servers, databases, file storage, etc.
* [**Sentry.**][sentry] A hosted error-tracking service, that happens to
  be open source.

   [heroku]: https://www.heroku.com/what
   [reactjs]: https://thinkster.io/tutorials/what-exactly-is-react
   [sentry]: https://sentry.io/about/
   [redis]: https://redis.io/topics/introduction
   [rails]: http://guides.rubyonrails.org/getting_started.html
   [swagger]: https://swagger.io/
   [docker]: https://www.docker.com/what-container
   [postgres]: https://www.postgresql.org/about/
   [aws]: https://aws.amazon.com/what-is-aws/
   [ansible]: https://networklore.com/ansible/
   [versionista]: https://versionista.com/about
   [ia]: https://archive.org/about/
   [webpack]: https://webpack.js.org/concepts/
   [tornado]: http://www.tornadoweb.org/en/stable/
   [web-monitoring-db]: https://github.com/edgi-govdata-archiving/web-monitoring-db
   [beautifulsoup]: https://medium.freecodecamp.org/how-to-scrape-websites-with-python-and-beautifulsoup-5946935d93fe

## Project Goals

The purpose of the system is to enable analysts to quickly review monitored government websites in order to report on [__meaningful changes__](#identifying-meaningful-changes). The Website Monitoring automated system a.k.a. Scanner aims to make these changes easy to track, review, and report on.

Broadly speaking:
1. Scanner _receives periodic scrapes_ of target websites from archival sources.
2. **(Not yet implemented)** Scanner processes data to _sift out meaningful changes_ for volunteer analysts. 
3. Volunteers and experts work together to _further sift out meaningful changes_ and qualify them for journalists by writing reports.
4. Journalists _build narratives and amplify stories_ for the wider public.

## How to Help

The best way to get involved is to take a run through our onboarding
process, for which we rely on Trello. It's designed to be self-directed,
so you can run through it at your own pace. But don't worry -- along the
way, it will introduce you to the humans of EDGI's Web Monitoring
project! Yay humans!

[![Onboarding screenshot](http://i.imgur.com/JmFiMue.png)][onboarding]

We are currently revamping that process so check back soon for a link. In the meantime these developer onboarding videos, though long, will be useful.

[Developer Orientation](https://www.youtube.com/watch?v=ig8rjII0wkU&index=88&list=PLtsP3g9LafVtj6IOMk05aOh-DdpuqWhue&t=0s)

[Architecture Overview](https://youtu.be/HM3kv0XwJZc?t=42m11s)

### Where we work

* Say hi on our chat!
   * [Create](https://archivers-slack.herokuapp.com/) an account on Slack team.
   * Join us in the `#webmonitoring` channel.
* Attend a software development call.
   * [Join](https://edgi-video-call-landing-page.herokuapp.com/https://zoom.us/j/187414228) our call, every Wednesday at 12pm ET.
   * Zoom Meeting account is optional. See above link for details.
   * We keep [notes](https://drive.google.com/drive/u/0/folders/0BxkWFSoyVYI3YVZXY1JxVllFVkU) for all meetings.

## Project Overview

### Use Case

1. Access captured data (starting with HTML, later encompassing more types) from
   multiple archival sources including Versionista and the
   Internet Archive.
2. Compare versions of the same page over time --- potentially using multiple
   different strategies.
3. Automatically filter out "nonmeaningful" or repetitive changes: for example,
   the "Page Last Viewed" timestamp updated or the same news article was added
   to 100 pages from the same website.
4. Prioritize the changes most likely to be "meaningful," meaning that some
   item of importance to fact-based governance was deleted or changed in a
   harmful way.
5. Present changes to human analysts with useful visualizations and statistics
   to help them differentiate meaningful changes. Each user will have been
   assigned a "subdomain", a full or partial government domain that has been
   identified as relevant to fact-based governance.
6. Collect annotations from the analysts. Use this to flag changes for special
   attention from EDGI administrators. Also, use it to feed back into the
   filtering and prioritization process. 

### Architecture

See [ARCHITECTURE.md](https://github.com/edgi-govdata-archiving/web-monitoring/blob/master/ARCHITECTURE.md)

### Identifying "Meaningful Changes"

The vast majority of changes to web pages are not relevant to analysts and we want to avoid presenting those irrelevant changes to analysts at all. It is, of course, not trivial to identify "meaningful" changes immediately, and we expect that analysts will always be involved in a decision about whether some changes are "important" or not. However, as we expand from 10<sup>4</sup> to 10<sup>7</sup> web pages, we need to drastically reduce the number of pages that analysts look at. 

Some examples of **meaningless** changes: 
- it's not unusual for a page to have a view counter on the bottom. In this case, the page changes **by definition** every time you view it.
- many sites have "content sliders" or news feeds that update periodically. This change may be "meaningful", in that it's interesting to see news updates. But it's only interesting once, not (as is sometimes seen) 1000 or 10000 times.

An example of a **meaningful** change: 
- In February, we noticed a systematic replacement of the word "impact" with the word "effect" on one website. This change is very interesting because while "impact" and "effect" have similar meanings, "impact" is a **stronger** word. So, there is an effort being made to **weaken** the language on existing sites. Our question is in part: what tools would we need in order to have this change **flagged** by our tools and presented to the analyst as **potentially interesting**?

### Sample Data

[`example-data`](./example-data) contains examples of website changes:

- `falsepos-...` files are cases any filter should catch
- `truepos...` files are cases of changes we care about

This is a small but illustrative sample. Many more samples will be made
available as soon as possible.

## Code of Conduct

This repository falls under EDGI's [Code of Conduct](https://github.com/edgi-govdata-archiving/overview/blob/master/CONDUCT.md).

## Contributing

Don't forget to check out the "How To Help" section above.

See our [contributor guidelines](https://github.com/edgi-govdata-archiving/web-monitoring/blob/master/CONTRIBUTING.md).

This project wouldn’t exist without a lot of amazing people’s help. Thanks to the following for their work reviewing URL's, monitoring changes, writing [reports](https://envirodatagov.org/website-monitoring/), and a slew of so many other things!

<!-- ALL-CONTRIBUTORS-LIST:START -->
| Contributions | Name |
| ----: | :---- |
| [🔢](# "Content") | Chris Amoss |
| [🔢](# "Content") [📋](# "Organizer") [🤔](# "Ideas and Planning") | Maya Anjur-Dietrich |
| [🔢](# "Content") | Marcy Beck |
| [🔢](# "Content") [📋](# "Organizer") [🤔](# "Ideas and Planning") | Andrew Bergman |
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


## Sponsors & Partners

Finally, we want to give a huge thanks to partner organizations that have helped to support this project with their tools and services:

- [The David and Lucile Packard Foundation](https://www.packard.org)
- [Doris Duke Charitable Foundation](http://www.ddcf.org)
- [Amazon Web Services](https://aws.amazon.com/)
- [Sentry.io](https://sentry.io)
- [PageFreezer](https://www.pagefreezer.com)
- [Google Cloud Platform](https://cloud.google.com)
- [Google Summer of Code](https://summerofcode.withgoogle.com)
- [DataKind](http://www.datakind.org/)


## License & Copyright

Copyright (C) 2017 Environmental Data and Governance Initiative (EDGI) <br /> <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" /></a> Web Monitoring documentation is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>. See the [`LICENSE`](https://github.com/edgi-govdata-archiving/web-monitoring/blob/master/LICENSE) file for details.

   [onboarding]: https://trello.com/b/FCGGEaQq/edgi-web-monitoring-project-onboarding

