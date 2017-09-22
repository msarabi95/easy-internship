/**
 * Created by MSArabi on 8/23/17.
 */
angular.module("ei.leaves.directives", ["ei.leaves.models", "chart.js"])

.directive("leaveRequestResponseCard", ["$timeout", "LeaveRequestResponse", function ($timeout, LeaveRequestResponse) {
    return {
        restrict: 'E',
        scope: {
            request: "=leaveRequest",
            moveToPastRequests: "&onResponse"
        },
        templateUrl: "/static/app/directives/templates/leaves/leave-request-response-card.html?rel=1506114197759",
        link: function (scope, element, attrs) {

            scope.response = {};

            scope.labels = ["Confirmed", "Pending", "Unused"];
            scope.data = [
                scope.request.setting.confirmed_days,
                scope.request.setting.pending_days,
                scope.request.setting.remaining_days
            ];
            scope.options = {
                title: {display: true, text: scope.request.intern_name.split(" ")[0] + "'s " + scope.request.type.name + "s"},
                legend: {display: true, position: 'bottom', labels: {
                    boxWidth: 8,
                    fontSize: 8
                }},
                layout: {padding: 0},
                cutoutPercentage: 65
            };

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
}]);