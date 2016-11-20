/**
 * Created by MSArabi on 11/17/16.
 */
angular.module("ei.planner", ["ei.planner.models", "ei.leaves.models", "ei.utils", "djng.forms",
                            "ngResource", "ngRoute", "ngSanitize", "ui.bootstrap", "ui.select"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/", {
            templateUrl: "static/partials/intern/planner/month-list.html",
            controller: "MonthListCtrl"
        })
        .when("/planner/:month_id/", {
            templateUrl: "static/partials/intern/planner/month-detail.html",
            controller: "MonthDetailCtrl"
        })
        .when("/planner/:month_id/new/", {
            templateUrl: "planner/rotation-request-form/",
            controller: "RotationRequestCreateCtrl"
        })
        .when("/planner/:month_id/history/", {
            templateUrl: "static/partials/intern/planner/rotation-request-history.html",
            controller: "RotationRequestHistoryCtrl"
        })
        .when("/planner/:month_id/cancel/", {
            templateUrl: "static/partials/intern/planner/deletion-request.html",
            controller: "DeletionRequestCtrl"
        })

}])

.controller("MonthListCtrl", ["$scope", "loadWithRelated", "InternshipMonth", "Rotation", "RotationRequest", "RequestedDepartment", "Department", "Hospital", "Specialty", "LeaveType", "Leave", "LeaveRequest", "LeaveCancelRequest",
    function ($scope, loadWithRelated, InternshipMonth, Rotation, RotationRequest, RequestedDepartment, Department, Hospital, Specialty, LeaveType, Leave, LeaveRequest, LeaveCancelRequest) {
        $scope.moment = moment;

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

            // Load all details of occupied months
            angular.forEach(occupied, function (monthIndex) {
                // Load current rotation
                $scope.months[monthIndex].current_rotation = loadWithRelated($scope.months[monthIndex].current_rotation, Rotation, [
                    [{department: Department}, [
                        {specialty: Specialty},
                        {hospital: Hospital}
                    ]]
                ]);
                // Load current leaves, leave requests, and leave cancel requests
                $scope.months[monthIndex].current_leaves = loadWithRelated($scope.months[monthIndex].current_leaves, Leave, [{type: LeaveType}]);
                $scope.months[monthIndex].current_leave_requests = loadWithRelated($scope.months[monthIndex].current_leave_requests, LeaveRequest, [{type: LeaveType}]);
                $scope.months[monthIndex].current_leave_cancel_requests = loadWithRelated($scope.months[monthIndex].current_leave_cancel_requests, LeaveCancelRequest);
            });

            // Load all details of requested month
            angular.forEach(requested, function (monthIndex) {
                $scope.months[monthIndex].current_request = loadWithRelated($scope.months[monthIndex].current_request, RotationRequest, [
                    {specialty: Specialty},
                    [{requested_department: RequestedDepartment}, [
                        [{department: Department}, [
                            {hospital: Hospital}
                        ]]
                    ]]
                ]);
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
}])

.controller("MonthDetailCtrl", ["$scope", "$routeParams", "loadWithRelated", "InternshipMonth", "Hospital", "Department", "Specialty", "Rotation", "RotationRequest", "RequestedDepartment", "RotationRequestResponse", "LeaveType", "Leave", "LeaveRequest", "LeaveRequestResponse", "LeaveCancelRequest",
    function ($scope, $routeParams, loadWithRelated, InternshipMonth, Hospital, Department, Specialty, Rotation, RotationRequest, RequestedDepartment, RotationRequestResponse, LeaveType, Leave, LeaveRequest, LeaveRequestResponse, LeaveCancelRequest) {
        $scope.moment = moment;

        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.month.$promise.then(function (month) {

            $scope.month.occupied = (month.current_rotation !== null);
            $scope.month.requested = (month.current_request !== null);

            if ($scope.month.occupied) {
                // Load current rotation
                $scope.month.current_rotation = loadWithRelated($scope.month.current_rotation, Rotation, [
                    [{department: Department}, [
                        {specialty: Specialty},
                        {hospital: Hospital}
                    ]],
                    [{rotation_request: RotationRequest}, [
                        {response: RotationRequestResponse}
                    ]]
                ]);
            }

            if ($scope.month.requested) {
                $scope.month.current_request = loadWithRelated($scope.month.current_request, RotationRequest, [
                    {specialty: Specialty},
                    [{requested_department: RequestedDepartment}, [
                        [{department: Department}, [
                            {hospital: Hospital}
                        ]]
                    ]]
                ]);
            }
            
            // Load current leaves, leave requests, and leave cancel requests
            $scope.month.current_leaves = loadWithRelated($scope.month.current_leaves, Leave, [{type: LeaveType}, [{request: LeaveRequest}, [{response: LeaveRequestResponse}]]]);
            $scope.month.current_leave_requests = loadWithRelated($scope.month.current_leave_requests, LeaveRequest, [{type: LeaveType}]);
            $scope.month.current_leave_cancel_requests = loadWithRelated($scope.month.current_leave_cancel_requests, LeaveCancelRequest);

        })

}])

.controller("RotationRequestCreateCtrl", ["$scope", "$routeParams", "$location", "Specialty", "Hospital", "Department",
    "RequestedDepartment", "RotationRequest", "InternshipMonth", "djangoForm", "$http", "$compile", "AcceptanceSettings",
    function ($scope, $routeParams, $location, Specialty, Hospital, Department, RequestedDepartment, RotationRequest, InternshipMonth, djangoForm, $http, $compile, AcceptanceSettings) {
        $scope.internshipMonth = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.disableHospitalMenu = true;
        $scope.rotationRequestData = {};
        $scope.specialties = Specialty.query();

        $scope.$watch('rotationRequestData.department_specialty', function (newValue, oldValue) {
            if (newValue !== oldValue) {
                $scope.disableHospitalMenu = true;
                if (newValue !== undefined && newValue !== "") {
                    $scope.getDepartments();
                } else {
                    $scope.rotationRequestData = {};  // reset form when specialty selection is changed
                }
            }
        });

        $scope.getDepartments = function () {
            // Load hospital data, each with the department corresponding to the selected specialty

            $scope.hospitals = Hospital.query(function (hospitals) {
                angular.forEach(hospitals, function (hospital, index) {
                    $scope.hospitals[index].department = Department.get_by_specialty_and_hospital({
                        specialty: $scope.rotationRequestData.department_specialty,
                        hospital: $scope.hospitals[index].id
                    });

                    $scope.hospitals[index].department.$promise.then(function (department) {
                        // Get acceptance settings
                        $scope.hospitals[index].department.acceptance_settings = AcceptanceSettings.get({}, {
                            department: department.id,
                            month: $scope.internshipMonth.month
                        });
                        $scope.hospitals[index].department.acceptance_settings.$promise.then(
                            function (settings) {
                                /*console.log(settings);*/
                            },
                            function (error) {
                                if (error.status !== 404) {
                                    toastr.error(error.statusText);
                                    console.error(error.statusText);
                                }
                            });
                    }, function (error) {
                        if (error.status !== 404) {
                            toastr.error(error.statusText);
                            console.error(error.statusText);
                        }
                    });

                });

                $scope.disableHospitalMenu = false;
            });
        };

        $scope.$watch('rotationRequestData.department_hospital', function (newValue, oldValue) {
            // Show or hide department detail fields based on whether department info is present in db or not
            if (newValue !== undefined && newValue !== oldValue) {
                var hospital = $scope.hospitals.find(function (obj, index) {
                    return obj.id == newValue;
                });

                if (!!hospital.department.id) {
                    var department = hospital.department;
                    $scope.rotationRequestData.department = department.id;
                    $scope.rotationRequestData.is_in_database = true;
                } else {
                    $scope.rotationRequestData.is_in_database = false;
                }
            }
        });

        $scope.$watch('rotationRequestForm.$message', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== "") {
                toastr.warning(newValue);
                $scope.rotationRequestForm.$message = undefined;
            }
        });

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
                }).error(function (error) {
                    console.log(error);
                    toastr.error(error);
                })
            }

            return false;
        };

        $scope.moment = moment;

}])

.controller("RotationRequestHistoryCtrl", ["$scope", "$routeParams", "loadWithRelated", "InternshipMonth", "RotationRequest", "RotationRequestResponse", "Specialty", "RequestedDepartment", "Department", "Hospital",
    function ($scope, $routeParams, loadWithRelated, InternshipMonth, RotationRequest, RotationRequestResponse, Specialty, RequestedDepartment, Department, Hospital) {
        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.month.$promise.then(function (month) {

            $scope.month.request_history = loadWithRelated(month.request_history, RotationRequest, [
                {specialty: Specialty},
                {response: RotationRequestResponse},
                [{requested_department: RequestedDepartment}, [
                    [{department: Department}, [
                        {hospital: Hospital}
                    ]]
                ]]
            ]);

        });
}])

.controller("DeletionRequestCtrl", ["$scope", "$routeParams", "$location", "InternshipMonth",
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