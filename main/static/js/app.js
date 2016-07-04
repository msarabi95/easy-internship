/**
 * Created by MSArabi on 6/16/16.
 */
var app = angular.module("easyInternship", ["djng.urls", "djng.rmi", "ngRoute", "ui.bootstrap"]);

const MonthStatus = {
    UNOCCUPIED: "Unoccupied",
    OCCUPIED: "Occupied",
    REQUESTED_UNOCCUPIED: "RequestedUnoccupied",
    REQUESTED_OCCUPIED: "RequestedOccupied"
};

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

    // TODO: Document following methods
    $scope.hasRotation = function (monthIndex) {
        var month = $scope.months[monthIndex];
        return (month.currentRotation != null);
    };

    $scope.hasRequest = function (monthIndex) {
        var month = $scope.months[monthIndex];
        return (month.currentRequest != null);
    };

    // Month status checkers

    $scope.isUnoccupied = function (monthIndex) {
        return (!$scope.hasRotation(monthIndex) && !$scope.hasRequest(monthIndex));
    };

    $scope.isOccupied = function (monthIndex) {
        return ($scope.hasRotation(monthIndex) && !$scope.hasRequest(monthIndex));
    };

    $scope.isRequestedUnoccupied = function (monthIndex) {
        return (!$scope.hasRotation(monthIndex) && $scope.hasRequest(monthIndex));
    };

    $scope.isRequestedOccupied = function (monthIndex) {
        return ($scope.hasRotation(monthIndex) && $scope.hasRequest(monthIndex));
    };

    function getMonthStatus(monthIndex) {
        if ($scope.isUnoccupied(monthIndex)) {
            return MonthStatus.UNOCCUPIED;
        } else if ($scope.isOccupied(monthIndex)) {
            return MonthStatus.OCCUPIED;
        } else if ($scope.isRequestedUnoccupied(monthIndex)) {
            return MonthStatus.REQUESTED_UNOCCUPIED;
        } else if ($scope.isRequestedOccupied(monthIndex)) {
            return MonthStatus.REQUESTED_OCCUPIED;
        }
    }

    // View type checkers

    $scope.rotationViewUnoccupied = function (monthIndex) {
        return $scope.isUnoccupied(monthIndex);
    };

    $scope.rotationViewOccupied = function (monthIndex) {
        return $scope.isOccupied(monthIndex);
    };

    $scope.rotationViewReqUnoccupied = function (monthIndex) {
        var month = $scope.months[monthIndex];
        return ($scope.isRequestedUnoccupied(monthIndex) && month.showRequest != true);
    };

    $scope.requestViewReqUnoccupied = function (monthIndex) {
        var month = $scope.months[monthIndex];
        return ($scope.isRequestedUnoccupied(monthIndex) && month.showRequest == true);
    };

    $scope.rotationViewReqOccupied= function (monthIndex) {
        var month = $scope.months[monthIndex];
        return ($scope.isRequestedOccupied(monthIndex) && month.showRequest != true);
    };

    $scope.requestViewUpdateReqOccupied = function (monthIndex) {
        var month = $scope.months[monthIndex];
        return ($scope.isRequestedOccupied(monthIndex) && month.showRequest == true && month.currentRequest.delete != true);
    };

    $scope.requestViewCancelReqOccupied = function (monthIndex) {
        var month = $scope.months[monthIndex];
        return ($scope.isRequestedOccupied(monthIndex) && month.showRequest == true && month.currentRequest.delete == true);
    };

    $scope.rotationView = function (monthIndex) {
        return ($scope.rotationViewUnoccupied(monthIndex) || $scope.rotationViewOccupied(monthIndex) || $scope.rotationViewReqUnoccupied(monthIndex) || $scope.rotationViewReqOccupied(monthIndex));
    };

    $scope.requestView = function (monthIndex) {
        return ($scope.requestViewReqUnoccupied(monthIndex) || $scope.requestViewUpdateReqOccupied(monthIndex) || $scope.requestViewCancelReqOccupied(monthIndex));
    };

    $scope.toggleShowRequest = function (monthIndex) {
        var month = $scope.months[monthIndex];
        if (month.showRequest == undefined) {
            month.showRequest = true;
        } else {
            month.showRequest = !month.showRequest;
        }
    };

    $scope.showModal = function (monthIndex) {
        var modalTemplates = {};
        modalTemplates[MonthStatus.UNOCCUPIED] = "partials/planner/modal-unoccupied.html";
        modalTemplates[MonthStatus.OCCUPIED] = "partials/planner/modal-occupied.html";
        modalTemplates[MonthStatus.REQUESTED_UNOCCUPIED] = "partials/planner/modal-requested-unoccupied.html";
        modalTemplates[MonthStatus.REQUESTED_OCCUPIED] = "partials/planner/modal-requested-occupied.html";

        var template = modalTemplates[getMonthStatus(monthIndex)];

        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: template,
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
