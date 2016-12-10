/**
 * Created by MSArabi on 7/31/16.
 */
angular.module("easyInternship", ["ei.utils"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/", {
            templateUrl: "static/partials/outsider/index.html"
        });

}]);
