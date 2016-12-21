/**
 * Created by MSArabi on 6/16/16.
 */
angular.module("easyInternship", ["ei.hospitals", "ei.months", "ei.rotations", "ei.leaves", "ei.utils",
                                  "ngRoute", "ngAnimate"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/", {
            templateUrl: "static/partials/intern/index.html?v=0002"
        })

}]);
