/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.months", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                              "ei.utils", "djng.forms", "ngAnimate", "ngResource", "ngRoute", "ngSanitize",
                              "ui.bootstrap", "ui.select", "ei.months.directives"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/", {
            templateUrl: "static/partials/intern/months/month-list.html?v=0006",
            controller: "MonthListCtrl"
        })
        .when("/planner/:month_id/", {
            templateUrl: "static/partials/intern/months/month-detail.html?v=0008",
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

.controller("MonthListCtrl", ["$scope", "Internship", function ($scope, Internship) {
    $scope.internship = Internship.query(function (internships) {
        $scope.internship = internships[0];
    });
}])

.controller("MonthDetailCtrl", ["$scope", "$location", "$routeParams", "Internship", "loadWithRelated", "InternshipMonth", "Hospital", "Department", "Specialty", "Rotation", "RotationRequest", "RequestedDepartment", "RotationRequestResponse", "RotationRequestForward", "LeaveType", "Leave", "LeaveRequest", "LeaveRequestResponse", "LeaveCancelRequest",
    function ($scope, $location, $routeParams, Internship, loadWithRelated, InternshipMonth, Hospital, Department, Specialty, Rotation, RotationRequest, RequestedDepartment, RotationRequestResponse, RotationRequestForward, LeaveType, Leave, LeaveRequest, LeaveRequestResponse, LeaveCancelRequest) {
        $scope.internship = Internship.query(function (internships) {
            $scope.internship = internships[0];
            console.log($scope.internship);
            $scope.month = $scope.internship.months.filter(function (month, index) {
                return month.month == $routeParams.month_id;
            })[0];
            $scope.month.occupied = ($scope.month.current_rotation !== null);
            $scope.month.requested = ($scope.month.current_rotation_request !== null);

            if ($scope.month.requested) {
                $scope.month.current_rotation_request.submission_datetime = moment($scope.month.current_rotation_request.submission_datetime);

                if (!!$scope.month.current_rotation_request.forward) {
                    $scope.month.current_rotation_request.forward.forward_datetime =
                        moment($scope.month.current_rotation_request.forward.forward_datetime);
                }
            }
        });

        // $scope.moment = moment;
        //
        // $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});
        //
        // $scope.month.$promise.then(function (month) {
        //
        //     $scope.month.occupied = (month.current_rotation !== null);
        //     $scope.month.requested = (month.current_rotation_request !== null);
        //
        //     if ($scope.month.occupied) {
        //         // Load current rotation
        //         $scope.month.current_rotation = loadWithRelated($scope.month.current_rotation, Rotation, [
        //             [{department: Department}, [
        //                 {specialty: Specialty},
        //                 {hospital: Hospital}
        //             ]],
        //             [{rotation_request: RotationRequest}, [
        //                 {response: RotationRequestResponse}
        //             ]]
        //         ]);
        //     }
        //
        //     if ($scope.month.requested) {
        //         $scope.month.current_rotation_request = loadWithRelated($scope.month.current_rotation_request, RotationRequest, [
        //             {specialty: Specialty},
        //             [{requested_department: RequestedDepartment}, [
        //                 [{department: Department}, [
        //                     {hospital: Hospital}
        //                 ]]
        //             ]]
        //         ]);
        //         $scope.month.current_rotation_request.$promise.then(function (request) {
        //             if (!!$scope.month.current_rotation_request.forward) {
        //                 $scope.month.current_rotation_request.forward = RotationRequestForward.get({id: request.forward});
        //             }
        //         });
        //     }
        //
        //     // Load current leaves, leave requests, and leave cancel requests
        //     $scope.month.current_leaves = loadWithRelated($scope.month.current_leaves, Leave, [{type: LeaveType}, [{request: LeaveRequest}, [{response: LeaveRequestResponse}]]]);
        //     $scope.month.current_leave_requests = loadWithRelated($scope.month.current_leave_requests, LeaveRequest, [{type: LeaveType}]);
        //     $scope.month.current_leave_cancel_requests = loadWithRelated($scope.month.current_leave_cancel_requests, LeaveCancelRequest);
        //
        // });

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