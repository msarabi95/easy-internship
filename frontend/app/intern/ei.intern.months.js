/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.months", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                              "ei.utils", "djng.forms", "ngAnimate", "ngResource", "ngRoute", "ngSanitize",
                              "ui.bootstrap", "ui.select"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/", {
            templateUrl: "static/partials/intern/months/month-list.html?v=0004",
            controller: "MonthListCtrl"
        })
        .when("/planner/:month_id/", {
            templateUrl: "static/partials/intern/months/month-detail.html?v=0005",
            controller: "MonthDetailCtrl"
        })
        .when("/planner/:month_id/freeze/", {
            templateUrl: function (params) {
                return "/api/internship_months/" + params[0] + "/request_freeze/";
            },
            controller: "FreezeRequestCreateCtrl"
        })
        .when("/planner/:month_id/freeze/cancel/", {
            templateUrl: "static/partials/intern/months/freeze-cancel-request-create.html",
            controller: "FreezeCancelRequestCreateCtrl"
        })

}])

.controller("MonthListCtrl", ["$scope", "$q", "loadWithRelated", "InternshipMonth", "Rotation", "RotationRequest", "RequestedDepartment", "Department", "Hospital", "Specialty", "Location", "LeaveType", "Leave", "LeaveRequest", "LeaveCancelRequest",
    function ($scope, $q, loadWithRelated, InternshipMonth, Rotation, RotationRequest, RequestedDepartment, Department, Hospital, Specialty, Location, LeaveType, Leave, LeaveRequest, LeaveCancelRequest) {
        $scope.moment = moment;

        $scope.months = InternshipMonth.query();

        $scope.months.$promise.then(function (results) {
            // Save the indices of occupied and requested months in 2 separate arrays
            angular.forEach(results, function (month, index) {
                var promises = [];

                // Load current rotation
                $scope.months[index].current_rotation = loadWithRelated($scope.months[index].current_rotation, Rotation, [
                    {specialty: Specialty},
                    {hospital: Hospital},
                    {location: Location}
                ]);

                if ($scope.months[index].current_rotation) {promises.push($scope.months[index].current_rotation.$promise)}

                // Load current rotation request
                $scope.months[index].current_rotation_request = loadWithRelated($scope.months[index].current_rotation_request, RotationRequest, [
                    {specialty: Specialty},
                    {hospital: Hospital},
                    {location: Location}
                ]);

                if ($scope.months[index].current_rotation_request) {promises.push($scope.months[index].current_rotation_request.$promise)}

                // No need to load rotation cancel request

                // No need to load freezes

                // Load current leaves, leave requests, and leave cancel requests
                //$scope.months[index].current_leaves = loadWithRelated($scope.months[index].current_leaves, Leave, [{type: LeaveType}]);
                //$scope.months[index].current_leave_requests = loadWithRelated($scope.months[index].current_leave_requests, LeaveRequest, [{type: LeaveType}]);
                //$scope.months[index].current_leave_cancel_requests = loadWithRelated($scope.months[index].current_leave_cancel_requests, LeaveCancelRequest);

                $scope.months[index].$promise = $q.all(promises)
            });
        });

        $scope.getTileClass = function (month) {
            if (!month.disabled && !month.frozen) {
                if (!month.occupied && !(month.has_rotation_request || month.has_rotation_cancel_request)) {
                    if (!month.has_freeze_request) {
                        return "default";
                    } else {
                        return "warning";
                    }
                } else if (!month.occupied && (month.has_rotation_request || month.has_rotation_cancel_request)) {
                    return "warning";
                } else if (month.occupied && !(month.has_rotation_request || month.has_rotation_cancel_request)) {
                    return "primary";
                //} else if (month.occupied && month.has_rotation_cancel_request) {
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

.controller("MonthDetailCtrl", ["$scope", "$location", "$routeParams", "loadWithRelated", "InternshipMonth", "Hospital", "Specialty", "Location", "Rotation", "RotationRequest", "RotationCancelRequest", "RotationRequestResponse", "RotationRequestForward", "Freeze", "FreezeRequest", "FreezeRequestResponse", "FreezeCancelRequest", "LeaveType", "Leave", "LeaveRequest", "LeaveRequestResponse", "LeaveCancelRequest",
    function ($scope, $location, $routeParams, loadWithRelated, InternshipMonth, Hospital, Specialty, Location, Rotation, RotationRequest, RotationCancelRequest, RotationRequestResponse, RotationRequestForward, Freeze, FreezeRequest, FreezeRequestResponse, FreezeCancelRequest, LeaveType, Leave, LeaveRequest, LeaveRequestResponse, LeaveCancelRequest) {
        $scope.moment = moment;

        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.month.$promise.then(function (month) {

            if ($scope.month.occupied) {
                // Load current rotation
                $scope.month.current_rotation = loadWithRelated($scope.month.current_rotation, Rotation, [
                    {specialty: Specialty},
                    {hospital: Hospital},
                    {location: Location},
                    [{rotation_request: RotationRequest}, [
                        {response: RotationRequestResponse}
                    ]]
                ]);
            }

            if ($scope.month.frozen) {
                // Load current freeze
                $scope.month.current_freeze = loadWithRelated($scope.month.current_freeze, Freeze, [
                    [{freeze_request: FreezeRequest}, [
                        {response: FreezeRequestResponse}
                    ]]
                ])
            }

            if ($scope.month.has_rotation_request) {
                $scope.month.current_rotation_request = loadWithRelated($scope.month.current_rotation_request, RotationRequest, [
                    {specialty: Specialty},
                    {hospital: Hospital},
                    {location: Location},
                    {forward: RotationRequestForward}
                ]);
            }
            
            if ($scope.month.has_rotation_cancel_request) {
                $scope.month.current_rotation_cancel_request = loadWithRelated($scope.month.current_rotation_cancel_request, RotationCancelRequest);
            }

            if ($scope.month.has_freeze_request) {
                $scope.month.current_freeze_request = loadWithRelated($scope.month.current_freeze_request, FreezeRequest);
            }

            if ($scope.month.has_freeze_cancel_request) {
                $scope.month.current_freeze_cancel_request = loadWithRelated($scope.month.current_freeze_cancel_request, FreezeCancelRequest);
            }

            // Load current leaves, leave requests, and leave cancel requests
            $scope.month.current_leaves = loadWithRelated($scope.month.current_leaves, Leave, [{type: LeaveType}, [{request: LeaveRequest}, [{response: LeaveRequestResponse}]]]);
            $scope.month.current_leave_requests = loadWithRelated($scope.month.current_leave_requests, LeaveRequest, [{type: LeaveType}]);
            $scope.month.current_leave_cancel_requests = loadWithRelated($scope.month.current_leave_cancel_requests, LeaveCancelRequest);

            console.log($scope.month);

        });

        $scope.record_response = function (is_approved, comments) {
            $scope.month.current_request.$respond({is_approved: is_approved, comments: comments}, function () {
                $location.path("/planner/" + $scope.month.month + "/history/");
            }, function (error) {
                toastr.error(error);
            });
        };

}])

.controller("FreezeRequestCreateCtrl", ["$scope", "$http", "$routeParams", "$location", "djangoForm", "InternshipMonth", function ($scope, $http, $routeParams, $location, djangoForm, InternshipMonth) {
    $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

    $scope.submit = function () {

        if ($scope.freezeRequestData) {

            $scope.freezeRequestData.month = $routeParams.month_id;

            $http.post(
                "/api/internship_months/" + $scope.month.month + "/request_freeze/",
                $scope.freezeRequestData
            ).success(function (out_data) {
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

.controller("FreezeCancelRequestCreateCtrl", ["$scope", "$routeParams", "$location", "InternshipMonth", function ($scope, $routeParams, $location, InternshipMonth) {
    $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

    $scope.submit = function () {

        $scope.month.$request_freeze_cancel({}, function (data) {
            $location.path("/planner");
        }, function (error) {
            toastr.error(error.statusText);
        });

    };
}]);