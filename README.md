SublimeJSCoverage
=================

Displays inline coverage report: Super + Shift + C

Plugin tries to find the latest coverage report in a closest "coverage" directory.

Karama should be configured to put coverage report to coverage directory, e.g:

```javascript
reporters: ['coverage'],
...

plugins : [
...
  'karma-coverage'
...
];

...

preprocessors: {
  // source files, that you wanna generate coverage for
  // do not include tests or libraries
  // (these files will be instrumented by Istanbul)
  'public/js/*.js': ['coverage']
},

...

//configure the reporter
coverageReporter: {
  type : 'html',
  dir : 'coverage/'
}
```
