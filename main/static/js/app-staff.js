/**
 * Created by MSArabi on 7/14/16.
 */
var app = angular.module("easyInternship", ["djng.urls", "djng.rmi", "ngRoute", "ngResource", "ui.bootstrap"]);

app.config(["$httpProvider", "$routeProvider", "djangoRMIProvider", "$resourceProvider",
    function ($httpProvider, $routeProvider, djangoRMIProvider, $resourceProvider) {

    // These settings enable Django to receive Angular requests properly.
    // Check:
    // http://django-angular.readthedocs.io/en/latest/integration.html#xmlhttprequest
    // http://django-angular.readthedocs.io/en/latest/csrf-protection.html#cross-site-request-forgery-protection
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    djangoRMIProvider.configure(tags);

    $routeProvider
        .when("/", {
            // This redirects users from / to /#/
            redirectTo: "/"
        })
        .when("/planner/", {
            templateUrl: "partials/planner/staff/index.html",
            controller: "MyCtrl"
        })

    $resourceProvider.defaults.stripTrailingSlashes = false;

}]);

app.factory("PlanRequest", ["$resource", function($resource) {
    // Refer to: https://www.sitepoint.com/creating-crud-app-minutes-angulars-resource/
    return $resource('/api/plan_requests/:id');
}]);

app.factory("RotationRequest", ["$resource", function($resource) {
    // Refer to: https://www.sitepoint.com/creating-crud-app-minutes-angulars-resource/
    return $resource('/api/rotation_requests/:id/', {id: '@id'}, {
      respond: {method:'POST', url: '/api/rotation_requests/respond/'}
    });
}]);

app.controller("MyCtrl", ["$scope", "PlanRequest", "RotationRequest", "$resource",
                            function ($scope, PlanRequest, RotationRequest, $resource) {
    $scope.planRequests = PlanRequest.query(function () {
        console.log($scope.planRequests);
    });

    $scope.selectPlanRequest = function (requestId) {
        $scope.selectedPlanRequest = PlanRequest.get({id: requestId}, function () {
            for (var i = 0; i < $scope.selectedPlanRequest.rotation_requests.length; i++) {
                var id = $scope.selectedPlanRequest.rotation_requests[i];
                $scope.selectedPlanRequest.rotation_requests[i] = RotationRequest.get({id: id});
            }
        });
    };

    $scope.approve = function (rotationRequest) {
        var response = RotationRequest.respond({id: rotationRequest.id, is_approved: true, comments: ""}, function () {
            rotationRequest.status = response.status;
        });
    };

    $scope.decline = function (rotationRequest) {
        var response = RotationRequest.respond({id: rotationRequest.id, is_approved: false, comments: ""}, function () {
            rotationRequest.status = response.status;
        });
    };
}]);