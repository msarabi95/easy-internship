/**
 * Created by MSArabi on 11/17/16.
 */
angular.module("ei.leaves", ["ngRoute"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/:month_id/leaves/new/", {
            templateUrl: "partials/leaves/intern/leave-request-create.html",
            controller: "LeaveRequestCreateCtrl"
        })
        .when("/planner/:month_id/leaves/history/", {
            templateUrl: "partials/leaves/intern/leave-request-history.html",
            controller: "LeaveRequestHistoryCtrl"
        })

}])

.controller("LeaveRequestCreateCtrl", ["$scope", function ($scope) {

}])

.controller("LeaveRequestHistoryCtrl", ["$scope", function ($scope) {

}]);