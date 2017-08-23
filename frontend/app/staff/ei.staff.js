/**
 * Created by MSArabi on 7/14/16.
 */
angular.module("easyInternship", ["ei.staff.accounts", "ei.staff.hospitals", "ei.staff.rotations", "ei.staff.leaves",
                                  "ei.months.models", "ei.rotations.models", "ei.accounts.models",
                                  "ei.utils", "ngRoute"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/", {
            redirectTo: "/interns/"
        });

}]);