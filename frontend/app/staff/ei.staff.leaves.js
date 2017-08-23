/**
 * Created by MSArabi on 8/15/17.
 */
angular.module("ei.staff.leaves", ["ngRoute", "ei.leaves.models", "ei.leaves.directives"])

.config(["$routeProvider", function ($routeProvider) {
    $routeProvider
        .when("/leaves/", {
            templateUrl: "/static/partials/staff/leaves/leave-request-list.html",
            controller: "LeaveRequestListCtrl"
        })
}])

.controller("LeaveRequestListCtrl", ["$scope", "LeaveRequest", function ($scope, LeaveRequest) {
    $scope.requests = LeaveRequest.query();


}]);