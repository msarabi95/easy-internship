/**
 * Created by MSArabi on 3/3/17.
 */
angular.module("ei.months.directives", ["ei.months.models"])

.directive("freezeRequestResponseCard", ["$timeout", "FreezeRequestResponse", function ($timeout, FreezeRequestResponse) {
    return {
        restrict: 'E',
        scope: {
            request: "=freezeRequest",
            moveToPastRequests: "&onResponse"
        },
        templateUrl: "/static/app/directives/templates/months/freeze-request-response-card.html?v=0001",
        link: function (scope, element, attrs) {

            scope.response = {};

            scope.flag = function (flagName) {
                scope.flags = {};  // reset all flags
                scope.flags[flagName] = true;

                $timeout(function () {try {scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
            };

            scope.respond = function (request, is_approved, comments) {
                var response = new FreezeRequestResponse({
                    request: request.id,
                    is_approved: is_approved,
                    comments: comments
                });

                response.$save(function () {
                     scope.moveToPastRequests({request: request});
                }, function (error) {
                    toastr.error(error);
                });

            };

        }
    }
}])

.directive("freezeCancelRequestResponseCard", ["$timeout", "FreezeCancelRequestResponse", function ($timeout, FreezeCancelRequestResponse) {
    return {
        restrict: 'E',
        scope: {
            request: "=freezeCancelRequest",
            moveToPastRequests: "&onResponse"
        },
        templateUrl: "/static/app/directives/templates/months/freeze-cancel-request-response-card.html",
        link: function (scope, element, attrs) {

            scope.response = {};

            scope.flag = function (flagName) {
                scope.flags = {};  // reset all flags
                scope.flags[flagName] = true;

                $timeout(function () {try {scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
            };

            scope.respond = function (request, is_approved, comments) {
                var response = new FreezeCancelRequestResponse({
                    request: request.id,
                    is_approved: is_approved,
                    comments: comments
                });

                response.$save(function () {
                     scope.moveToPastRequests({request: request});
                }, function (error) {
                    toastr.error(error);
                });
            };

        }
    }
}]);