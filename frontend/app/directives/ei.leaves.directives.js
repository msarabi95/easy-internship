/**
 * Created by MSArabi on 8/23/17.
 */
angular.module("ei.leaves.directives", ["ei.leaves.models"])

.directive("leaveRequestResponseCard", ["$timeout", "LeaveRequestResponse", function ($timeout, LeaveRequestResponse) {
    return {
        restrict: 'E',
        scope: {
            request: "=leaveRequest",
            moveToPastRequests: "&onResponse"
        },
        templateUrl: "/static/app/directives/templates/leaves/leave-request-response-card.html",
        link: function (scope, element, attrs) {

            scope.response = {};

            scope.flag = function (flagName) {
                scope.flags = {};  // reset all flags
                scope.flags[flagName] = true;

                $timeout(function () {try {scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
            };

            scope.respond = function (request, is_approved, comments) {
                var response = new LeaveRequestResponse({
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