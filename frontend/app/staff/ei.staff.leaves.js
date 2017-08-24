/**
 * Created by MSArabi on 8/15/17.
 */
angular.module("ei.staff.leaves", ["ngRoute", "ei.leaves.models", "ei.leaves.directives"])

.config(["$routeProvider", function ($routeProvider) {
    $routeProvider
        .when("/leaves/", {
            templateUrl: "/static/partials/staff/leaves/leave-request-list.html?rel=1503603970309",
            controller: "LeaveRequestListCtrl"
        })
}])

.controller("LeaveRequestListCtrl", ["$scope", "LeaveRequest", function ($scope, LeaveRequest) {
    $scope.requests = LeaveRequest.query();

    $scope.reverseOptions = [
        {label: "Ascending", value: false},
        {label: "Descending", value: true}
    ];

    $scope.orderingOptions = [
        {label: "Submission date and time", value: function (request) {return request.submission_datetime.toDate();}},
        {label: "Leave type", value: function (request) {return request.type.name;}},
        {label: "Name", value: function (request) {return request.intern_name;}},
    ];

    $scope.ordering = {
        option: $scope.orderingOptions[0].value,
        reverse: false
    };

    $scope.removeRequest = function (request) {
        var index = $scope.requests.indexOf(request);
        if (index > -1) {
            $scope.requests.splice(index, 1);
        }
    };
}]);