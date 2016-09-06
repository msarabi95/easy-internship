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
            templateUrl: "partials/planner/new-request.html",
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
    "RequestedDepartment", "RotationRequest", "InternshipMonth",
    function ($scope, $routeParams, $location, Specialty, Hospital, Department, RequestedDepartment, RotationRequest, InternshipMonth) {
        $scope.internshipMonth = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.specialties = Specialty.query();
        $scope.hospitals = Hospital.query();

        $scope.requested_department_data = {};

        $scope.getDepartment = function () {
            // This function is called whenever the hospital or specialty fields are updated
            if (!!$scope.specialty && !!$scope.hospital) {

                $scope.department = Department.get_by_specialty_and_hospital({
                    specialty: $scope.specialty,
                    hospital: $scope.hospital
                }, function (department) {
                    $scope.new_department = false;
                }, function (error) {
                    if (error.status == 404) {
                        $scope.new_department = true;
                    } else {
                        toastr.error(error.statusText);
                        console.log(error);
                    }
                });
            }
        };

        $scope.submit = function () {
            // This function submits the new rotation request

            $scope.rotationRequestForm.errors = {};

            console.log($scope.rotationRequestForm);

            if ($scope.new_department == true) {
                $scope.requested_department_data.is_in_database = false;
                $scope.requested_department_data.department = null;

                $scope.requested_department_data.department_specialty = parseInt($scope.specialty);
                $scope.requested_department_data.department_hospital = parseInt($scope.hospital);

            } else {
                $scope.requested_department_data = {
                    is_in_database: true,
                    department: $scope.department.id
                }
            }

            $scope.requested_department = new RequestedDepartment($scope.requested_department_data);

            $scope.requested_department.$save(function (requested_department) {

                $scope.rotation_request = new RotationRequest({
                    month: $scope.internshipMonth.month,
                    specialty: $scope.specialty,
                    requested_department: requested_department.id
                });
                $scope.rotation_request.$submit(function (rotation_request) {
                    $location.path("/planner");
                }, function (error) {
                    if (error.status == 400) {

                        angular.forEach(error.data, function (fieldErrors, key) {
                            $scope.rotationRequestForm[key].$setValidity("required", false);
                            $scope.rotationRequestForm.errors[key] = fieldErrors;
                        });

                        toastr.warning("There are some isssues with your submission. Please resolve them and try submitting again.")

                    } else {
                        toastr.error(error.statusText);
                    }
                    console.log(error);
                });

            }, function (error) {
                toastr.error(error.statusText);
                console.log(error);
            });
        }

}]);
