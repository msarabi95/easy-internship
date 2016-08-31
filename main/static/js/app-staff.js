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

    // Check for messages with each response
    $httpProvider.interceptors.push(function ($q, $rootScope) {
       return {
           'response': function (response) {
               if ( $rootScope.fetchingMessages != true ) {
                   $rootScope.fetchingMessages = true;
                   $rootScope.$broadcast("fetchMessages");
               }
               return response;
           },
           'responseError': function (rejection) {
               if ( $rootScope.fetchingMessages != true ) {
                   $rootScope.fetchingMessages = true;
                   $rootScope.$broadcast("fetchMessages");
               }
               return $q.reject(rejection);
           }
       };
    });

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

app.run(function ($rootScope, $resource) {
    toastr.options.positionClass = "toast-top-center";
    $rootScope.$on("fetchMessages", getMessages);

    function getMessages(event, eventData) {
        var messages = $resource("messages").query(function (messages) {
            $rootScope.fetchingMessages = false;
            for (var i = 0; i < messages.length; i++) {
                toastr[messages[i].level_tag](messages[i].message);
            }
        });
    }

    $rootScope.fetchingMessages = true;
    getMessages("", {});
});

app.controller("MenuCtrl", ["$scope", "$route", "$location", function ($scope, $route, $location) {
    $scope.isActive = function (viewLocation) {
        return viewLocation == "#" + $location.path();
    }
}]);

app.factory("PlanRequest", ["$resource", function($resource) {
    // Refer to: https://www.sitepoint.com/creating-crud-app-minutes-angulars-resource/
    return $resource('/api/plan_requests/:id', {id: '@id'});
}]);

app.factory("RotationRequest", ["$resource", function($resource) {
    // Refer to: https://www.sitepoint.com/creating-crud-app-minutes-angulars-resource/
    return $resource('/api/rotation_requests/:id/', {id: '@id'}, {
      respond: {method:'POST', url: '/api/rotation_requests/respond/'},
      forward: {method:'POST', url: '/api/rotation_requests/forward/'}
    });
}]);

app.controller("MyCtrl", ["$scope", "PlanRequest", "RotationRequest", "$resource",
function ($scope, PlanRequest, RotationRequest, $resource) {
    function getPlanRequests() {
        $scope.planRequests = PlanRequest.query();

        if (!!$scope.selectedPlanRequest) {
            var currentPR = PlanRequest.get({id: $scope.selectedPlanRequest.id}, function () {
                if (currentPR.is_closed) {
                    $scope.selectedPlanRequest = null;
                }
            });

        }
    }

    getPlanRequests();

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
            getPlanRequests(); // FIXME: There should be a better way than this
        });
    };

    $scope.decline = function (rotationRequest) {
        var response = RotationRequest.respond({id: rotationRequest.id, is_approved: false, comments: ""}, function () {
            rotationRequest.status = response.status;
            getPlanRequests(); // FIXME: There should be a better way than this
        });
    };

    $scope.forward = function (rotationRequest) {
        var response = RotationRequest.forward({id: rotationRequest.id}, function () {
            rotationRequest.status = response.status;
            getPlanRequests(); // FIXME: There should be a better way than this
        });
    };
}]);