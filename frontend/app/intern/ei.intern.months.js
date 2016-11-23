/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.months", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                              "ei.utils", "djng.forms", "ngResource", "ngRoute", "ngSanitize",
                              "ui.bootstrap", "ui.select"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/", {
            templateUrl: "static/partials/intern/months/month-list.html",
            controller: "MonthListCtrl"
        })
        .when("/planner/:month_id/", {
            templateUrl: "static/partials/intern/months/month-detail.html",
            controller: "MonthDetailCtrl"
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

}]);