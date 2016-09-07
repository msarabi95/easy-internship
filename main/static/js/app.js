/**
 * Created by MSArabi on 6/16/16.
 */
var app = angular.module("easyInternship", ["djng.forms", "ngResource", "ngRoute", "easy.planner"]);

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

    $resourceProvider.defaults.stripTrailingSlashes = false;

    $routeProvider
        .when("/", {
            // This redirects users from / to /#/
            redirectTo: "/"
        })
        .when("/planner/", {
            templateUrl: "partials/planner/planner-index.html",
            controller: "NewCtrl"
        })
        .when("/planner/:month_id/new/", {
            templateUrl: "planner/rotation-request-form/",
            controller: "NewRequestCtrl"
        })

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
    //$scope.currentTab = $route.current.currentTab;

    $scope.isActive = function (viewLocation) {
        return viewLocation == "#" + $location.path();
    }
}]);

app.controller("NewCtrl", ["$scope", "InternshipMonth", "Rotation", "RotationRequest", "Department", "Hospital",
    function ($scope, InternshipMonth, Rotation, RotationRequest, Department, Hospital) {
        $scope.months = InternshipMonth.query();

        $scope.months.$promise.then(function (results) {

            var occupied = [];
            var requested = [];

            // Save the indices of occupied and requested months in 2 separate arrays
            angular.forEach(results, function (month, index) {
                if (month.current_rotation !== null) {
                    occupied.push(index);
                }
                if (month.current_request !== null) {
                    requested.push(index);
                }
            });

            // Load all details of occupied months
            angular.forEach(occupied, function (monthIndex) {
                // Load current rotation
                $scope.months[monthIndex].current_rotation = Rotation.get({id: $scope.months[monthIndex].current_rotation});

                $scope.months[monthIndex].current_rotation.$promise.then(function (rotation) {
                    // Load current rotation department
                    $scope.months[monthIndex].current_rotation.department =
                        Department.get({id: rotation.department});

                    $scope.months[monthIndex].current_rotation.department.$promise.then(function (department) {
                        // Load current rotation hospital
                        $scope.months[monthIndex].current_rotation.department.hospital =
                            Hospital.get({id: department.hospital});
                    })
                })
            });

            console.log($scope.months);
        });
}]);

app.controller("NewRequestCtrl", ["$scope", "$routeParams", "$location", "Specialty", "Hospital", "Department",
    "RequestedDepartment", "RotationRequest", "InternshipMonth", "djangoForm", "$http", "$compile",
    function ($scope, $routeParams, $location, Specialty, Hospital, Department, RequestedDepartment, RotationRequest, InternshipMonth, djangoForm, $http, $compile) {
        $scope.internshipMonth = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.$watchGroup(['rotationRequestData.department_specialty','rotationRequestData.department_hospital'],
            function () {
                $scope.getDepartment();
        });

        $scope.$watch('rotationRequestForm.$message', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== "") {
                toastr.warning(newValue);
                $scope.rotationRequestForm.$message = undefined;
            }
        });

        $scope.getDepartment = function () {
            // This function is called whenever the hospital or specialty fields are updated
            if (!!$scope.rotationRequestData.department_specialty && !!$scope.rotationRequestData.department_hospital) {

                $scope.department = Department.get_by_specialty_and_hospital({
                    specialty: $scope.rotationRequestData.department_specialty,
                    hospital: $scope.rotationRequestData.department_hospital
                }, function (department) {
                    $scope.rotationRequestData.department = department.id;
                    $scope.rotationRequestData.is_in_database = true;
                }, function (error) {
                    if (error.status == 404) {
                        $scope.rotationRequestData.is_in_database = false;
                    } else {
                        toastr.error(error.statusText);
                        console.log(error);
                    }
                });
            }
        };

        $scope.submit = function () {
            if ($scope.rotationRequestData) {

                $scope.rotationRequestData.month = $routeParams.month_id;

                $http.post(
                    "/planner/rotation-request-form/",
                    $scope.rotationRequestData
                ).success(function (out_data) {
                    if (!djangoForm.setErrors($scope.rotationRequestForm, out_data.errors)) {
                        $location.path("/planner");
                    }
                }).error(function (out_data) {
                    toastr.error(out_data);
                })
            }

            return false;
        }

}]);
