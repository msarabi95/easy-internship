/**
 * Created by MSArabi on 12/18/16.
 */
angular.module("ei.rotations.directives", ["ei.utils"])

.directive("rotationRequestCard", ["$timeout", function ($timeout) {
    return {
        restrict: 'E',
        scope: {
            request: "=rotationRequest",
            moveToPastRequests: "&onResponse",
            moveToForwardedRequests: "&onForward"
        },
        templateUrl: "/static/directive-templates/staff/rotations/rotation-request-card.html",
        link: function (scope, element, attrs) {
            scope.flag = function (flagName) {
                scope.flags = {};  // reset all flags
                scope.flags[flagName] = true;
    
                $timeout(function () {try {scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
            };
    
            scope.respond = function (request, response, comments) {
                request.$respond({is_approved: response, comments: comments}, function (data) {
                    scope.moveToPastRequests({request: request});
                }, function (error) {
                    toastr.error(error);
                });
            };
    
            scope.forward = function (request) {
                request.$forward({}, function (data) {
                    scope.moveToForwardedRequests({request: request});
                }, function (error) {
                    toastr.error(error);
                });
            };
        }
    }
}])

.directive("acceptanceList", ["$timeout", function ($timeout) {
    return {
        restrict: 'E',
        scope: {
            list: "=list",
            removeFromList: "&onResponse"
        },
        templateUrl: "/static/directive-templates/staff/rotations/acceptance-list.html",
        link: function (scope, element, attrs) {
            scope.respondAll = function () {
                scope.loading = true;
                scope.list.$respond({}, function () {
                    scope.loading = false;
                    scope.removeFromList({list: scope.list});
                });
                //$timeout(function() {
                //
                //}, 2000);
            };
        }
    }
}]);