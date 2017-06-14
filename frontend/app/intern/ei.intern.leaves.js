/**
 * Created by MSArabi on 11/17/16.
 */
angular.module("ei.leaves", ["ngRoute", "ngFileUpload", "ui.select", "ei.utils", "ui.bootstrap", "ei.accounts.models",
                             "ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/:month_id/request-leave/", {
            templateUrl: "static/partials/intern/leaves/request-leave.html?v=0001",
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

.controller("LeaveRequestCreateCtrl", ["$scope", "$routeParams", "Upload", "$location", "User", "LeaveType", "LeaveSetting",
    function ($scope, $routeParams, Upload, $location, User, LeaveType, LeaveSetting) {
        User.query(function (users) {
            $scope.intern = users[0];
        });

        $scope.month = moment({
            year: Math.floor($routeParams.month_id / 12),
            month: ($routeParams.month_id % 12)
        });
        $scope.leaveTypes = LeaveType.query();
        $scope.leaveSettings = LeaveSetting.query();

        $scope.leave_request = {};

        $scope.startDateOptions = $scope.endDateOptions = {
            minDate: $scope.month.toDate(),
            maxDate: moment($scope.month).endOf('month').toDate(),
            initDate: $scope.month.toDate(),
            maxMode: 'day',
            showWeeks: false
        };

        $scope.submit = function () {

            var data = $scope.leave_request;
            data.intern = $scope.intern.id;
            data.month = $scope.month.year() * 12 + ($scope.month.month());
            data.start_date = moment(data.start_date).format('YYYY-MM-DD');
            data.end_date = moment(data.end_date).format('YYYY-MM-DD');

            // Submit
            $scope.upload = Upload.upload({
                url: '/api/leave_requests/',
                data: data,
                method: "POST"
            });
            $scope.upload.then(function (resp) {
                $location.path('/planner');

            }, function (resp) {
                if (resp.status !== 400) {
                    console.log(resp);
                    toastr.error(resp);
                } else {
                    $scope.leave_request_form.$message = resp.data.non_field_errors;
                    const fields = ['type', 'start_date', 'end_date'];
                    for (var i in fields) {
                        var item = fields[i];
                        if (!$scope.leave_request_form[item]) {
                            continue;
                        }

                        $scope.leave_request_form[item].$message = resp.data[item];
                        if (!!$scope.leave_request_form[item].$message) {
                            $scope.leave_request_form[item].$setPristine(true);
                        }
                    }
                }
            });

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