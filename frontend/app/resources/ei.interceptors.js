/**
 * Created by MSArabi on 12/9/16.
 */
angular.module("ei.interceptors", [])

.factory("DateTimeFieldToMomentInterceptor", ["$q", function ($q) {
    return function (fields) {
        if (typeof fields !== typeof []) {
            throw "Invalid argument: Fields should be an array."
        }
        return {
            response: function (response) {

                // Check if response is an array (as in a `query` call)
                if (Array.isArray(response.resource)) {
                    for (var idx = 0; idx < response.resource.length; idx++) {
                        for (var fIdx in fields) {
                            var field = fields[fIdx];
                            if (response.resource[idx].hasOwnProperty(field)) {
                                response.resource[idx][field] = moment(response.resource[idx][field]);
                            } else {
                                throw "Invalid field name."
                            }
                        }
                    }
                } else { // Otherwise, if response is a single object
                    for (var idx in fields) {
                        var field = fields[idx];
                        if (response.resource.hasOwnProperty(field)) {
                            response.resource[field] = moment(response.resource[field]);
                        } else {
                            throw "Invalid field name."
                        }
                    }
                }

                // Return response resource
                // Check this: https://github.com/angular/angular.js/issues/11201#issuecomment-76367339
                return response.resource;
            }
        }
    }
}]);