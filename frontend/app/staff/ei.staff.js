/**
 * Created by MSArabi on 7/14/16.
 */
angular.module("easyInternship", ["ei.staff.accounts", "ei.staff.hospitals", "ei.staff.rotations",
                                  "ei.months.models", "ei.rotations.models", "ei.accounts.models",
                                  "ei.utils", "ngRoute"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/", {
            // This redirects users from / to /#/
            redirectTo: "/recent/"
        })
        .when("/recent/", {
            templateUrl: "static/partials/staff/index.html",
            controller: "ListRecentRequestsCtrl"
        });

}])

.controller("ListRecentRequestsCtrl", ["$scope", "Internship", "RotationRequest", "Intern", "Profile",
    function ($scope, Internship, RotationRequest, Intern, Profile) {
        $scope.internships = Internship.with_unreviewed_requests();

        $scope.internships.$promise.then(function (internships) {
            angular.forEach(internships, function (internship, index) {
                // Load the intern profile and standard profile
                $scope.internships[index].intern = Intern.get({id: internship.intern});
                $scope.internships[index].intern.$promise.then(function (intern) {
                    $scope.internships[index].intern.profile = Profile.get({id: intern.profile});
                });

                // Load rotation requests
                angular.forEach(internship.rotation_requests, function (request_id, request_id_index) {
                    $scope.internships[index].rotation_requests[request_id_index] = RotationRequest.get({id: request_id});
                });

            });
        });
}]);