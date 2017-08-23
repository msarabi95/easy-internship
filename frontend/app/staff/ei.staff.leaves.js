/**
 * Created by MSArabi on 8/15/17.
 */
angular.module("ei.staff.leaves", ["ngRoute", "ei.leaves.models", "ei.leaves.directives"])

.config(["$routeProvider", function ($routeProvider) {
    $routeProvider
        .when("/leaves/", {
            templateUrl: "/static/partials/staff/leaves/leave-request-list.html?v=0001",
            controller: "LeaveRequestListCtrl"
        })
}])

.controller("LeaveRequestListCtrl", ["$scope", "LeaveRequest", function ($scope, LeaveRequest) {
    $scope.requests = LeaveRequest.query();

    $scope.removeRequest = function (request) {
        var index = $scope.requests.indexOf(request);
        if (index > -1) {
            $scope.requests.splice(index, 1);
        }
    };
}]);