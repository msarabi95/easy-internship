/**
 * Created by MSArabi on 7/31/16.
 */
var app = angular.module("easyInternship", ["djng.urls", "djng.rmi", "ngRoute", "ngResource", "ui.bootstrap", "ngFileUpload"]);

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
        .when("/forward/:key/", {
            templateUrl: "partials/planner/outsider/forward-details.html",
            controller: "MyCtrl"
        })

    $resourceProvider.defaults.stripTrailingSlashes = false;

}]);

app.factory("Forward", ["$resource", function($resource) {
    // Refer to: https://www.sitepoint.com/creating-crud-app-minutes-angulars-resource/
    return $resource('/api/rotation_request_forwards/:key', {key: '@key'}, {
        respond: {method:'POST', url: '/api/rotation_request_forwards/respond/'}
    });
}]);

app.controller("MyCtrl", ["$scope", "$routeParams", "Forward", "Upload", function ($scope, $routeParams, Forward, Upload) {

    function getForward() {
        var f = Forward.get({key: $routeParams.key}, function () {
            $scope.forward = f;
        }, function (response) {
            if (response.status === 404) {
                $scope.incorrectKey = true;
            }
        });
    };

    getForward();

    $scope.response = {};

    //$scope.respond = function () {
    //    var response = $scope.response;
    //    console.log($scope.response);
    //    response.key = $scope.forward.key;
    //    Forward.respond(response, function (result) {
    //        console.log(result);
    //    });
    //};

    // upload later on form submit or something similar
    $scope.submit = function() {
      if ($scope.response.response_memo) {
        $scope.upload($scope.response.response_memo);
      }
    };

    // upload on file select or drop
    $scope.upload = function (file) {
        var data = $scope.response;
        data.key = $scope.forward.key;
        data.response_memo = file;

        Upload.upload({
            url: '/api/rotation_request_forwards/respond/',
            data: data,
            method: "POST"
        }).then(function (resp) {
            console.log('Success ' + resp.config.data.response_memo.name + 'uploaded. Response: ' + resp.data);
            // refresh forward info
            getForward();
        }, function (resp) {
            console.log('Error status: ' + resp.status);
        });
    };
}]);