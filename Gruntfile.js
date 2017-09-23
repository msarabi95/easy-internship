module.exports = function(grunt) {

    grunt.initConfig({
	    pkg: grunt.file.readJSON('package.json'),
	    cachebreaker: {
	        // NOTE: In order to have cache busted properly, html cache busting is run first, then js
            // => it has to be run twice
			html: {
				options: {
					match: (function () {
					    var exec = require('child_process').execSync;

                        try {
                        	var htmlChanges = exec('git status --porcelain | grep -E "M frontend/(partials|app/directives)/.*\.html$"', {encoding: 'utf8'});
                        	var htmlArray = htmlChanges.split("\n").slice(0, -1); // Skip new line at end of file
                            var matchArray = [];

                            // Prepare HTML file match strings
                            for (var i = 0; i < htmlArray.length; i++) {
                                var a = htmlArray[i].split(" M ")[1];
                                var b = a.split("frontend/")[1];
                                var c = "static/" + b;
                                matchArray.push(c);
                            }

                            return matchArray;
                        } catch (e) {
                            if (e.cmd === 'git status --porcelain | grep -E "M frontend/(partials|app/directives)/.*\.html$"' && e.status === 1) {
                                return [];
                            } else {
                                throw e;  // Do not prevent real errors from being thrown
                            }
                        }
					})()
				},
				files: {
				    src: (function() {
				        var exec = require('child_process').execSync;
				        var jsFiles = exec('find ./frontend/app -type f -regex ".*\.js$"', {encoding: 'utf8'});
				        var jsArray = jsFiles.split("\n").slice(0, -1); // Skip new line at EOF

                        return jsArray;
                    })()
				}
			},
            js: {
			    options: {
					match: (function () {
					    var exec = require('child_process').execSync;

					    try {
					        var jsChanges = exec('git status --porcelain | grep "M frontend/app/.*\.js$"', {encoding: 'utf8'});
                            var jsArray = jsChanges.split("\n").slice(0, -1); // Skip new line at end of file

                            var matchArray = [];

                            // Prepare JS file match strings
                            for (var j = 0; j < jsArray.length; j++) {
                                var x = jsArray[j].split(" M ")[1];
                                var y = x.split("frontend/")[1];
                                var z = "\{% static \'" + y + "\' %\}";
                                matchArray.push(z);
                            }

                            return matchArray;
                        } catch (e) {
					        if (e.cmd === 'git status --porcelain | grep "M frontend/app/.*\.js$"' && e.status === 1) {
                                return [];
                            } else {
                                throw e;  // Do not prevent real errors from being thrown
                            }
                        }
					})()
				},
				files: {
				    src: ['./easy_internship/templates/components/scripts.html']
				}
            }
	    }
	});
    
    grunt.loadNpmTasks('grunt-cache-breaker');
    
};
