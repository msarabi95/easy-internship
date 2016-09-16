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
            templateUrl: "partials/planner/intern/month-list.html",
            controller: "MonthListCtrl"
        })
        .when("/planner/:month_id/", {
            templateUrl: "partials/planner/intern/month-detail.html",
            controller: "MonthDetailCtrl"
        })
        .when("/planner/:month_id/new/", {
            templateUrl: "planner/rotation-request-form/",
            controller: "RotationRequestCreateCtrl"
        })
        .when("/planner/:month_id/history/", {
            templateUrl: "partials/planner/intern/rotation-request-history.html",
            controller: "RotationRequestHistoryCtrl"
        })
        .when("/planner/:month_id/cancel/", {
            templateUrl: "partials/planner/intern/deletion-request.html",
            controller: "DeletionRequestCtrl"
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

app.controller("MonthListCtrl", ["$scope", "InternshipMonth", "Rotation", "RotationRequest", "RequestedDepartment", "Department", "Hospital", "Specialty",
    function ($scope, InternshipMonth, Rotation, RotationRequest, RequestedDepartment, Department, Hospital, Specialty) {
        $scope.months = InternshipMonth.query();

        $scope.months.$promise.then(function (results) {

            var occupied = [];
            var requested = [];

            // Save the indices of occupied and requested months in 2 separate arrays
            // Also add 2 flags (occupied and requested) with the appropriate boolean values to each month object
            angular.forEach(results, function (month, index) {
                if (month.current_rotation !== null) {
                    occupied.push(index);
                    $scope.months[index].occupied = true;
                } else {
                    $scope.months[index].occupied = false;
                }

                if (month.current_request !== null) {
                    requested.push(index);
                    $scope.months[index].requested = true;
                } else {
                    $scope.months[index].requested = false;
                }
            });

            console.log(occupied);
            console.log($scope.months[occupied[0]]);

            // Load all details of occupied months
            angular.forEach(occupied, function (monthIndex) {
                // Load current rotation
                $scope.months[monthIndex].current_rotation = Rotation.get({id: $scope.months[monthIndex].current_rotation});

                $scope.months[monthIndex].current_rotation.$promise.then(function (rotation) {
                    // Load current rotation department
                    $scope.months[monthIndex].current_rotation.department =
                        Department.get({id: rotation.department});

                    $scope.months[monthIndex].current_rotation.department.$promise.then(function (department) {
                        // Load current rotation specialty
                        $scope.months[monthIndex].current_rotation.department.specialty =
                            Specialty.get({id: department.specialty});

                        // Load current rotation hospital
                        $scope.months[monthIndex].current_rotation.department.hospital =
                            Hospital.get({id: department.hospital});
                    })
                })
            });

            // Load all details of requested months
            angular.forEach(requested, function (monthIndex) {
                $scope.months[monthIndex].current_request = RotationRequest.get({id: $scope.months[monthIndex].current_request});

                $scope.months[monthIndex].current_request.$promise.then(function (request) {
                    // Load current request specialty
                    $scope.months[monthIndex].current_request.specialty =
                        Specialty.get({id: request.specialty});

                    // Load current request requested department
                    $scope.months[monthIndex].current_request.requested_department =
                        RequestedDepartment.get({id: request.requested_department});

                    $scope.months[monthIndex].current_request.requested_department.$promise.then(function (requested_department) {
                       // Load department object
                       $scope.months[monthIndex].current_request.requested_department.department =
                           Department.get({id: requested_department.department});

                       $scope.months[monthIndex].current_request.requested_department.department.$promise.then(function (department) {
                           $scope.months[monthIndex].current_request.requested_department.department.hospital =
                               Hospital.get({id: department.hospital});
                       })
                    });
                })
            })

        });

        $scope.getTileClass = function (month) {
            if (!month.occupied && !month.requested) {
                return "default";
            } else if (!month.occupied && month.requested) {
                return "warning";
            } else if (month.occupied && !month.requested) {
                return "primary";
            //} else if (month.occupied && month.requested && month.current_request.delete) {
            //    return "danger";
            } else {
                return "primary";
            }
        };
}]);

app.controller("MonthDetailCtrl", ["$scope", "$routeParams", "InternshipMonth", "Hospital", "Department", "Specialty", "Rotation", "RotationRequest", "RequestedDepartment", "RotationRequestResponse",
    function ($scope, $routeParams, InternshipMonth, Hospital, Department, Specialty, Rotation, RotationRequest, RequestedDepartment, RotationRequestResponse) {
        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.month.$promise.then(function (month) {

            $scope.month.occupied = (month.current_rotation !== null);
            $scope.month.requested = (month.current_request !== null);

            if ($scope.month.occupied) {
                // Load current rotation
                $scope.month.current_rotation = Rotation.get({id: $scope.month.current_rotation});

                $scope.month.current_rotation.$promise.then(function (rotation) {
                    // Load current rotation department
                    $scope.month.current_rotation.department =
                        Department.get({id: rotation.department});

                    $scope.month.current_rotation.department.$promise.then(function (department) {
                        // Load current rotation hospital
                        $scope.month.current_rotation.department.specialty =
                            Specialty.get({id: department.specialty});

                        // Load current rotation hospital
                        $scope.month.current_rotation.department.hospital =
                            Hospital.get({id: department.hospital});
                    })

                    $scope.month.current_rotation.rotation_request =
                        RotationRequest.get({id: rotation.rotation_request});

                    $scope.month.current_rotation.rotation_request.$promise.then(function (rotation_request) {
                        $scope.month.current_rotation.rotation_request.response =
                            RotationRequestResponse.get({id: rotation_request.response});
                    })
                })
            }

            if ($scope.month.requested) {
                $scope.month.current_request = RotationRequest.get({id: $scope.month.current_request});

                $scope.month.current_request.$promise.then(function (request) {
                    // Load current request specialty
                    $scope.month.current_request.specialty =
                        Specialty.get({id: request.specialty});

                    // Load current request requested department
                    $scope.month.current_request.requested_department =
                        RequestedDepartment.get({id: request.requested_department});

                    $scope.month.current_request.requested_department.$promise.then(function (requested_department) {
                       // Load department object
                       $scope.month.current_request.requested_department.department =
                           Department.get({id: requested_department.department});

                       $scope.month.current_request.requested_department.department.$promise.then(function (department) {
                           $scope.month.current_request.requested_department.department.hospital =
                               Hospital.get({id: department.hospital});
                       })
                    });
                })
            }

        })



}]);

app.controller("RotationRequestCreateCtrl", ["$scope", "$routeParams", "$location", "Specialty", "Hospital", "Department",
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

app.controller("RotationRequestHistoryCtrl", ["$scope", "$routeParams", "InternshipMonth", "RotationRequest", "RotationRequestResponse", "Specialty", "RequestedDepartment", "Department", "Hospital",
    function ($scope, $routeParams, InternshipMonth, RotationRequest, RotationRequestResponse, Specialty, RequestedDepartment, Department, Hospital) {
        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.month.$promise.then(function (month) {

            // Load the rotation request history
            angular.forEach(month.request_history, function (rotation_request, index) {
                $scope.month.request_history[index] = RotationRequest.get({id: rotation_request});

                $scope.month.request_history[index].$promise.then(function (rotation_request) {

                    console.log($scope.month);

                    $scope.month.request_history[index].specialty = Specialty.get({id: rotation_request.specialty});

                    $scope.month.request_history[index].response = RotationRequestResponse.get({id: rotation_request.response});

                    $scope.month.request_history[index].requested_department =
                        RequestedDepartment.get({id: rotation_request.requested_department});

                    $scope.month.request_history[index].requested_department.$promise.then(function (requested_department) {
                        $scope.month.request_history[index].requested_department.department =
                            Department.get({id: requested_department.department});

                        $scope.month.request_history[index].requested_department.department.$promise.then(function (department) {
                            $scope.month.request_history[index].requested_department.department.hospital =
                                Hospital.get({id: department.hospital});

                            console.log($scope.month);

                        })
                    })

                });
            });
        });
}]);

app.controller("DeletionRequestCtrl", ["$scope", "$routeParams", "$location", "InternshipMonth",
    function ($scope, $routeParams, $location, InternshipMonth) {
    $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

    $scope.submit = function () {

        $scope.month.$cancel_rotation({}, function (data) {
            $location.path("/planner");
        }, function (error) {
            toastr.error(error.statusText);
        });

    };
}]);