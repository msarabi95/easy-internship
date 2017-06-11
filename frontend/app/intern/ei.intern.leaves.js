/**
 * Created by MSArabi on 11/17/16.
 */
angular.module("ei.leaves", ["ngRoute", "djng.forms", "ui.select", "ei.utils",
                             "ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/:month_id/request-leave/", {
            templateUrl: "static/partials/intern/leaves/request-leave.html",
            controller: "LeaveRequestCreateCtrl"
        })
        .when("/planner/:month_id/leaves/history/", {
            templateUrl: "static/partials/intern/leaves/leave-request-history.html",
            controller: "LeaveRequestHistoryCtrl"
        })
        .when("/planner/:month_id/leaves/:leave_id/cancel/", {
            templateUrl: "static/partials/intern/leaves/request-leave-cancel.html",
            controller: "LeaveRequestCancelCtrl"
        })

}])

.controller("LeaveRequestCreateCtrl", ["$scope", "$http", "$routeParams", "$location", "djangoForm", "InternshipMonth", "LeaveType",
    function ($scope, $http, $routeParams, $location, djangoForm, InternshipMonth, LeaveType) {
        $scope.month = moment({
            year: Math.floor($routeParams.month_id / 12),
            month: ($routeParams.month_id % 12)
        });
        $scope.leaveTypes = LeaveType.query();

        $scope.startDateOptions = $scope.endDateOptions = {
            minDate: $scope.month.toDate(),
            maxDate: moment($scope.month).endOf('month').toDate(),
            initDate: $scope.month.toDate(),
            maxMode: 'day',
            showWeeks: false
        };

        $scope.$watch('leaveRequestData.start_date_as_date', function (newValue, oldValue) {
            if (newValue !== undefined) {
                $scope.leaveRequestData.start_date = moment(newValue).format('MM/DD/YYYY');
                $scope.endDateOptions.minDate = moment(newValue).toDate();
            }
        });

        $scope.$watch('leaveRequestData.end_date_as_date', function (newValue, oldValue) {
            if (newValue !== undefined) {
                $scope.leaveRequestData.end_date = moment(newValue).format('MM/DD/YYYY');
                $scope.startDateOptions.maxDate = moment(newValue).toDate();
            }
        });

        $scope.$watch('leaveRequestForm.$message', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== "") {
                toastr.warning(newValue);
                $scope.leaveRequestForm.$message = undefined;
            }
        });

        $scope.submit = function () {
            if ($scope.leaveRequestData) {

                $scope.leaveRequestData.month = $routeParams.month_id;

                $scope.submission = $http.post(
                    "/leaves/leave-request-form/",
                    $scope.leaveRequestData
                );
                $scope.submission.success(function (out_data) {
                    if (!djangoForm.setErrors($scope.leaveRequestForm, out_data.errors)) {
                        $location.path("/planner/" + $scope.month.month);
                    }
                }).error(function (error) {
                    console.log(error);
                    toastr.error(error);
                })
            }

            return false;
        };

}])

.controller("LeaveRequestHistoryCtrl", ["$scope", function ($scope) {

}])

.controller("LeaveRequestCancelCtrl", ["$scope", "$routeParams", "loadWithRelated", "InternshipMonth", "Leave", "LeaveType",
    function ($scope, $routeParams, loadWithRelated, InternshipMonth, Leave, LeaveType) {
        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});
        $scope.leave = loadWithRelated($routeParams.leave_id, Leave, [{type: LeaveType}]);

        $scope.submit = function () {

            //$scope.month.$cancel_rotation({}, function (data) {
            //    $location.path("/planner");
            //}, function (error) {
            //    toastr.error(error.statusText);
            //});

        };
}]);