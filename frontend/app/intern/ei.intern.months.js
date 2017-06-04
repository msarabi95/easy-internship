/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.months", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                              "ei.utils", "djng.forms", "ngAnimate", "ngResource", "ngRoute", "ngSanitize",
                              "ui.bootstrap", "ui.select", "ei.months.directives"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/", {
            templateUrl: "static/partials/intern/months/month-list.html?v=0005",
            controller: "MonthListCtrl"
        })
        .when("/planner/:month_id/", {
            templateUrl: "static/partials/intern/months/month-detail.html?v=0007",
            controller: "MonthDetailCtrl"
        })
        .when("/planner/:month_id/request-freeze/", {
            templateUrl: function (params) {
                return "/api/internship_months/" + params[0] + "/request_freeze/";
            },
            controller: "RequestFreezeCtrl"
        })
        .when("/planner/:month_id/cancel-freeze/", {
            templateUrl: "static/partials/intern/months/request-freeze-cancel.html",
            controller: "RequestFreezeCancelCtrl"
        })
        .when("/planner/:month_id/request-freeze/delete/", {
            templateUrl: "static/partials/intern/months/delete-freeze-request.html",
            controller: "DeleteFreezeRequestCtrl"
        })
        .when("/planner/:month_id/cancel-freeze/delete/", {
            templateUrl: "static/partials/intern/months/delete-freeze-cancel-request.html",
            controller: "DeleteFreezeCancelRequestCtrl"
        });

}])

.controller("MonthListCtrl", ["$scope", "loadWithRelated", "Intern", "InternshipMonth", "Rotation", "RotationRequest", "RequestedDepartment", "Department", "Hospital", "Specialty", "LeaveType", "Leave", "LeaveRequest", "LeaveCancelRequest",
    function ($scope, loadWithRelated, Intern, InternshipMonth, Rotation, RotationRequest, RequestedDepartment, Department, Hospital, Specialty, LeaveType, Leave, LeaveRequest, LeaveCancelRequest) {
        $scope.moment = moment;

        Intern.query(function (interns) {
            $scope.intern = interns[0];
        });
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

                if (month.current_rotation_request !== null) {
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
                $scope.months[monthIndex].current_rotation_request = loadWithRelated($scope.months[monthIndex].current_rotation_request, RotationRequest, [
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
            if (!month.disabled && !month.frozen) {
                if (!month.occupied && !month.requested) {
                    if (!month.current_freeze_request) {
                        return "default";
                    } else {
                        return "warning";
                    }
                } else if (!month.occupied && month.requested) {
                    return "warning";
                } else if (month.occupied && !month.requested) {
                    return "primary";
                //} else if (month.occupied && month.requested && month.current_rotation_request.delete) {
                //    return "danger";
                } else {
                    return "primary";
                }
            } else if (!!month.frozen) {
                return "info";
            } else {
                return "default";
            }

        };
}])

.controller("MonthDetailCtrl", ["$scope", "$location", "$routeParams", "loadWithRelated", "InternshipMonth", "Hospital", "Department", "Specialty", "Rotation", "RotationRequest", "RequestedDepartment", "RotationRequestResponse", "RotationRequestForward", "LeaveType", "Leave", "LeaveRequest", "LeaveRequestResponse", "LeaveCancelRequest",
    function ($scope, $location, $routeParams, loadWithRelated, InternshipMonth, Hospital, Department, Specialty, Rotation, RotationRequest, RequestedDepartment, RotationRequestResponse, RotationRequestForward, LeaveType, Leave, LeaveRequest, LeaveRequestResponse, LeaveCancelRequest) {
        $scope.moment = moment;

        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.month.$promise.then(function (month) {

            $scope.month.occupied = (month.current_rotation !== null);
            $scope.month.requested = (month.current_rotation_request !== null);

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
                $scope.month.current_rotation_request = loadWithRelated($scope.month.current_rotation_request, RotationRequest, [
                    {specialty: Specialty},
                    [{requested_department: RequestedDepartment}, [
                        [{department: Department}, [
                            {hospital: Hospital}
                        ]]
                    ]]
                ]);
                $scope.month.current_rotation_request.$promise.then(function (request) {
                    if (!!$scope.month.current_rotation_request.forward) {
                        $scope.month.current_rotation_request.forward = RotationRequestForward.get({id: request.forward});
                    }
                });
            }

            // Load current leaves, leave requests, and leave cancel requests
            $scope.month.current_leaves = loadWithRelated($scope.month.current_leaves, Leave, [{type: LeaveType}, [{request: LeaveRequest}, [{response: LeaveRequestResponse}]]]);
            $scope.month.current_leave_requests = loadWithRelated($scope.month.current_leave_requests, LeaveRequest, [{type: LeaveType}]);
            $scope.month.current_leave_cancel_requests = loadWithRelated($scope.month.current_leave_cancel_requests, LeaveCancelRequest);

        });

        $scope.record_response = function (is_approved, comments) {
            $scope.month.current_rotation_request.$respond({is_approved: is_approved, comments: comments}, function () {
                $location.path("/planner/" + $scope.month.month + "/history/");
            }, function (error) {
                toastr.error(error);
            });
        };

}])

.controller("RequestFreezeCtrl", ["$scope", "$http", "$routeParams", "$location", "djangoForm", "InternshipMonth", function ($scope, $http, $routeParams, $location, djangoForm, InternshipMonth) {
    $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

    $scope.submit = function () {

        if ($scope.freezeRequestData) {

            $scope.freezeRequestData.month = $routeParams.month_id;

            $scope.submission = $http.post(
                "/api/internship_months/" + $scope.month.month + "/request_freeze/",
                $scope.freezeRequestData
            );
            $scope.submission.success(function (out_data) {
                if (!djangoForm.setErrors($scope.freezeRequestForm, out_data.errors)) {
                    $location.path("/planner");
                }
            }).error(function (error) {
                console.log(error);
                toastr.error(error);
            });
        }

        return false;

    };
}])

.controller("RequestFreezeCancelCtrl", ["$scope", "$routeParams", "$location", "InternshipMonth", function ($scope, $routeParams, $location, InternshipMonth) {
    $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

    $scope.submit = function () {

        $scope.month.$request_freeze_cancel({}, function (data) {
            $location.path("/planner");
        }, function (error) {
            toastr.error(error.statusText);
        });

    };
}])

.controller("DeleteFreezeRequestCtrl", ["$scope", function ($scope) {
    // TODO
}])

.controller("DeleteFreezeCancelRequestCtrl", ["$scope", function ($scope) {
    // TODO
}]);