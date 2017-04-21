/**
 * Created by MSArabi on 6/16/16.
 */
angular.module("easyInternship", ["ei.hospitals", "ei.months", "ei.rotations", "ei.leaves", "ei.utils",
                                  "ei.accounts.models", "ngRoute", "ngAnimate"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/", {
            templateUrl: "static/partials/intern/index.html?v=0003",
            controller: "IndexCtrl"
        })

}])

.controller("IndexCtrl", ["$scope", "Intern", function ($scope, Intern) {
    Intern.query(function (interns) {
        $scope.intern = interns[0];
    });
}]);
