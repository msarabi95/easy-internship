/**
 * Created by MSArabi on 6/16/16.
 */
var app = angular.module("easyInternship", ["ngRoute"]);

app.controller("MyCtrl", ["$scope", function ($scope) {
    $scope.whatever = 1;
}]);

app.config(["$routeProvider", function ($routeProvider) {
    $routeProvider
        .when("/", {
        // This redirects users from / to /#/
        redirectTo: "/"
    })
        .when("/planner", {
        templateUrl: "partials/planner/partials/template.html",
        controller: "MyCtrl"
    })

}]);