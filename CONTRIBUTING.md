# Contributing Guidelines

We love improvements to our tools! EDGI has general [guidelines for contributing](https://github.com/edgi-govdata-archiving/overview/blob/master/CONTRIBUTING.md) and a [code of conduct](https://github.com/edgi-govdata-archiving/overview/blob/master/CONDUCT.md) for all of our organizational repos.

## Submitting Web Monitoring Issues

Issues that are project-wide, or relate heavily to the interaction between different components, should be added to our [Web Monitoring issue queue](https://github.com/edgi-govdata-archiving/web-monitoring/issues). Component-specific issues should be added to their respective repository.

## Code Style / Best Practices:

The following are recommend code styling and best practices for all the Web Monitoring repositories. We also have some best practices specifically for our [web-monitoring-ui](https://github.com/edgi-govdata-archiving/web-monitoring-ui/blob/master/CONTRIBUTING.md) repo.

### Naming:

*No abbreviations.* Abbreviations tend to overlap a lot between domains, so they can be very ambiguous and confusing. This is especially true for non-native English speakers, even if they are fluent. Exceptions for things that are primarily referred to by abbreviation _in common language_, e.g. “URL,” “FAQ,” “ID,” _not_ “utils,” “idx,” etc. Single-letter names are ok only in contexts where their value is totally arbitrary, e.g. `function compare (a, b)`, or in the rare places where their use is normal, e.g. `x/y/z` in math functions referring to points.

*If camel-casing, treat acronyms as a single word.* e.g. `parseHtml()`, not `parseHTML()`. This goes with the above—word boundaries can get easily confused when two acronyms run up against each other.

### Alphabetize imports at the start of files:

Keep it simple, just alphabetize at the top of the file.

### Spacing in code:

Overall, we recommend [Stroustrup](https://en.wikipedia.org/wiki/Indentation_style#Variant:_Stroustrup) spacing.

```js
if (foo) {
  bar();
}
else {
  baz();
}
```

### Commenting:

*Make sure to comment code.* Write doc comments for every public interface. If possible, try and make sure to do private ones, too. Make judicious use of non-doc comments, but focus on the _why_ of the code they precede, not the what or how (sometimes those are needed, too, but that is _often_ a sign the code could be better factored or a function could be better named—but not always, so never jump down someone’s throat about it). When in doubt about whether a comment is needed for clarity, add one.

*Make judicious use of **TODO**, **FIXME**, **HACK**, **NOTE**, **XXX** comments.* And always include a reason with them.
- **TODO**: this is incomplete, but s OK for now.
- **FIXME**: this is actually really broken, and if you have the time and knowledge to address it when you see it, please do so.
- **XXX**: _Do not ship this code._ (For us, that means don’t merge into master.) This can be used for a work-in-progress that’s not acceptable in its current state, but you needed to commit to save time, get feedback, or release some half-done work for someone else to finish.
- **HACK**: the way this is done is not great, but you can see no better way at the moment. Like **FIXME**, if you see this and have the time or know-how, fix it.
- **NOTE**: Be careful, there be dragons here. This code is delicate (or maybe hot), so this comment should denote things anyone touching the code must be aware of.

## Testing:

Behavior Driven Development is a good starting point. Writing tests in a whole other language is not necessary. We recommend the practice of having full-sentence test names, e.g. `it('should do something I care about', /* Test */);` and further breaking them into blocks with `describe('some behavior or component')`.

### Testing: it() or test():

We recommend it()

### Pull Requests with tests:

For Processing and DB repos, all pull requests require some test coverage.
For UI, it is not currently required. Note, we want to begin requiring it in the future, after the codebase has been factored to make testing a more realistic requirement.

## Process:

### Pull Request assignment:

Before starting to work on an issue, check for assigness. If no one is assignd to it, assign it to yourself. For new contributions, add a comment that you are working on it. If someone is assigned to it, but you don't see any activity on the issue, make a friendly inquire to see if it is actively being work on. 

### Upgrading 3rd party dependencies:

Keeping up to date with latest version of external packages, libraries, frameworks, etc is highly recommended. When a new release occurs, check to see if an issue to upgrade has been written. If it hasn’t, create an issue to begin a discussion on the best upgrade path.
