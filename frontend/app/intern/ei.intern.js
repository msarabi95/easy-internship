/**
 * Created by MSArabi on 6/16/16.
 */
angular.module("easyInternship", ["ei.months", "ei.rotations", "ei.leaves", "ei.utils", "ngRoute"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/", {
            templateUrl: "static/partials/intern/index.html"
        })

}]);
