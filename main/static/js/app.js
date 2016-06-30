/**
 * Created by MSArabi on 6/16/16.
 */
var app = angular.module("easyInternship", ["djng.urls", "djng.rmi", "ngRoute", "ui.bootstrap"]);

app.config(["$httpProvider", "$routeProvider", "djangoRMIProvider",
    function ($httpProvider, $routeProvider, djangoRMIProvider) {

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
            templateUrl: "partials/planner/planner-index.html",
            controller: "MyCtrl"
        })

}]);

app.controller("MyCtrl", ["$scope", "djangoUrl", "djangoRMI", "$uibModal", function ($scope, djangoUrl, djangoRMI, $uibModal) {
    djangoRMI.planner.planner_api.get_internship_info()
        .success(function (data) {
            console.log(data);
            $scope.internshipInfo = data;
        })
        .error(function (message) {
            // TODO: show an error notification
            console.log(message);
        });

    djangoRMI.planner.planner_api.get_possible_months()
        .success(function (data) {
            $scope.months = data;
        })
        .error(function (message) {
            // TODO: show an error notification
            console.log(message);
        });

    $scope.hasRotationOrRequest = function (monthIndex) {
        var month = $scope.months[monthIndex];
        return !!(month.currentRotation != null || month.currentRequest != null);
    };

    $scope.showModal = function (monthIndex) {
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: 'partials/planner/modal.html',
            controller: 'ModalInstanceCtrl',
            resolve: {
                'month': $scope.months[monthIndex]
            }
        });

        modalInstance.result.then(function (result) {
            console.log(result);
        }, function () {
            // Well, nothing should be done here...
        });
    };

}]);

app.controller("ModalInstanceCtrl", ["$scope", "djangoRMI", "$uibModalInstance", "month", function ($scope, djangoRMI, $uibModalInstance, month) {
    djangoRMI.planner.planner_api.get_hospitals_list()
        .success(function (data) {
            console.log(data);
            $scope.hospitals = data;
        })
        .error(function (message) {
            // TODO: show an error notification
            console.log(message);

        });

    $scope.month = month;

    $scope.ok = function () {
        $uibModalInstance.close("Hooray!");
    };

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    }
}]);
