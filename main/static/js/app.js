/**
 * Created by MSArabi on 6/16/16.
 */
var app = angular.module("easyInternship", ["djng.urls", "djng.rmi", "ngResource",
                                            "ngRoute", "ui.bootstrap", "easy.planner"]);

const MonthStatus = {
    UNOCCUPIED: "Unoccupied",
    OCCUPIED: "Occupied",
    REQUESTED_UNOCCUPIED: "RequestedUnoccupied",
    REQUESTED_OCCUPIED: "RequestedOccupied"
};

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

    $resourceProvider.defaults.stripTrailingSlashes = false;

    djangoRMIProvider.configure(tags);

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

app.controller("MyCtrl", ["$scope", "djangoUrl", "djangoRMI", "$uibModal", function ($scope, djangoUrl, djangoRMI, $uibModal) {
    function loadMonths() {
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
                if ($scope.months != undefined) {

                    // Preserve the value of the show request flag
                    for (var i = 0; i < data.length; i++) {
                        data[i].showRequest = $scope.months[i].showRequest;

                        $scope.months[i] = data[i];
                    }

                } else {
                    $scope.months = data;
                }
            })
            .error(function (message) {
                // TODO: show an error notification
                console.log(message);
            });
    }

    loadMonths();

    //function getMessages() {
    //    djangoRMI.planner.planner_api.get_messages()
    //        .success(function (data) {
    //            $scope.messages = data;
    //        })
    //        .error(function (message) {
    //            console.log(message);
    //        });
    //}
    //
    //getMessages();

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
                'month': $scope.months[monthIndex],
                'submitted': $scope.internshipInfo.currentPlanRequestSubmitted
            }
        });

        modalInstance.result.then(function (result) {

            var jobType = result.jobType;
            var requestData = result.requestData || {};

            requestData.month = $scope.months[monthIndex].month;

            console.log(requestData);

            requestData.delete = requestData.delete === 'true';

            console.log(requestData);

            if (jobType == "create") {
                //requestData.delete = false;  // FIXME

                djangoRMI.planner.planner_api.create_request(requestData)
                    .success(function (response) {
                        console.log("SUCCESS!");
                        loadMonths();
                    })
                    .error(function (message) {
                        console.log(message);
                    });
            } else if (jobType == "update") {
                //requestData.delete = false;  // FIXME

                djangoRMI.planner.planner_api.update_request(requestData)
                    .success(function (response) {
                        console.log("SUCCESS!");
                        loadMonths();
                    })
                    .error(function (message) {
                        console.log(message);
                    });

            } else if (jobType == "delete") {
                djangoRMI.planner.planner_api.delete_request(requestData)
                    .success(function (response) {
                        console.log("SUCCESS!");
                        loadMonths();
                    })
                    .error(function (message) {
                        console.log(message);
                    });
            }
        }, function () {
            // Well, nothing should be done here...
        });
    };

    $scope.submit = function () {
        djangoRMI.planner.planner_api.submit_plan_request()
            .success(function (data) {
                console.log("SUBMITTED? MAYBE.");
                //getMessages();
                loadMonths();
            })
            .error(function (message) {
                console.log(message);
            });
        //getMessages();
    };

}]);

app.controller("ModalInstanceCtrl", ["$scope", "djangoRMI", "$uibModalInstance", "month", "submitted", function ($scope, djangoRMI, $uibModalInstance, month, submitted) {
    djangoRMI.planner.planner_api.get_hospitals_list()
        .success(function (data) {
            $scope.hospitals = data;
        })
        .error(function (message) {
            // TODO: show an error notification
            console.log(message);

        });

    djangoRMI.planner.planner_api.get_specialties_list()
        .success(function (data) {
            $scope.specialties = data;
        }).error(function (message) {
            console.log(message);
        });

    $scope.month = month;
    $scope.submitted = submitted;
    $scope.unoccupiedDefaultTab = submitted ? 'request-history':'rotation-request';

    $scope.chosen = {};
    $scope.showDeleteConfirm = false;

    $scope.toggleDeleteConfirm = function () {
        $scope.showDeleteConfirm = !$scope.showDeleteConfirm;
    };

    $scope.showUpdateForm = false;
    $scope.toggleUpdateForm = function () {
        $scope.showUpdateForm = !$scope.showUpdateForm;
    };

    $scope.ok = function () {
        var jobType;
        if ($scope.showUpdateForm) {
            jobType = "update";
        } else {
            jobType = "create";
        }
        var data = {
            jobType: jobType,
            requestData: $scope.chosen
        };
        $uibModalInstance.close(data);
    };
    
    $scope.deleteRequest = function () {
        var data = {
            jobType: "delete"
        };
        $uibModalInstance.close(data);
    };

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    $scope.dismissDeletePopover = function () {
        $scope.popoverIsOpen = false;
    }
}]);
