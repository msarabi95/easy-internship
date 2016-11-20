/**
 * Created by MSArabi on 7/31/16.
 */
var app = angular.module("easyInternship", ["ngRoute", "ngResource", "ui.bootstrap", "ngFileUpload"]);

app.config(["$httpProvider", "$routeProvider", "$resourceProvider",
    function ($httpProvider, $routeProvider, $resourceProvider) {

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

    $routeProvider
        .when("/", {
            templateUrl: "static/partials/outsider/index.html",
            controller: "IndexCtrl"
        })
        .when("/forward/:key/", {
            templateUrl: "static/partials/outsider/planner/forward-details.html",
            controller: "MyCtrl"
        })

    $resourceProvider.defaults.stripTrailingSlashes = false;

}]);

app.run(function ($rootScope, $resource) {
    //toastr.options.positionClass = "content-wrapper";
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

app.factory("Forward", ["$resource", function($resource) {
    // Refer to: https://www.sitepoint.com/creating-crud-app-minutes-angulars-resource/
    return $resource('/api/rotation_request_forwards/:key', {key: '@key'}, {
        respond: {method:'POST', url: '/api/rotation_request_forwards/respond/'}
    });
}]);

app.controller("IndexCtrl", ["$scope", function ($scope) {
    $scope.slides = [
        {
            id: 1,
            image: "/static/img/ksauhs-admin-tower.jpg",
            text: "KSAUHS"
        }
    ]
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