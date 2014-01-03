SublimeMochaJSCoverage
=================

Highlights uncovered lines based on a json coverage file.

The file must be named coverage.json and placed at the root directory of the Sublime view. 

Commands:

* Display highlights: Super + Shift + C
* Remove highlights: Super + Shift + C + X

Using with Mocha
===================

You may need to install the JSCoverage plugin
```
npm install jscoverage
```

Run Mocha with the json-cov reporter, i.e.

```
mocha -R json-cov > coverage.json
```

Inspired by https://github.com/genbit/SublimeJSCoverage