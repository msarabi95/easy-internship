/**
 * Created by MSArabi on 11/17/16.
 */
angular.module("ei.leaves", ["ngRoute", "ngFileUpload", "ui.select", "ei.utils", "ui.bootstrap", "ei.accounts.models",
                             "ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                             "ei.rotations.directives"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/:month_id/request-leave/", {
            templateUrl: "static/partials/intern/leaves/request-leave.html?rel=1498228344438",
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

        $scope.leave_request = {
            start_date: $scope.month.toDate(),
            end_date: $scope.month.toDate()
        };

        $scope.startDateOptions = $scope.endDateOptions = {
            minDate: $scope.month.toDate(),
            maxDate: moment($scope.month).endOf('month').toDate(),
            initDate: $scope.month.toDate(),
            maxMode: 'day',
            showWeeks: false
        };

        $scope.returnDateOptions = Object.assign({}, $scope.endDateOptions);

        $scope.$watch('leave_request.type', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== oldValue) {
                $scope.selectedSetting = $scope.leaveSettings.filter(function (setting) {
                    return setting.type.id == newValue;
                })[0];
            }
        });

        $scope.$watch('leave_request.end_date', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== oldValue) {
                var endDate = moment(newValue);
                var dayOfWeek = endDate.isoWeekday();  // https://momentjs.com/docs/#/get-set/iso-weekday/
                const sunday = 7, thursday = 4, friday = 5;
                // Add 1 to 3 days, depending on whether the end date is a Thursday, Friday, or another
                // day of the week (to skip the weekend)
                var add = (dayOfWeek === thursday || dayOfWeek === friday) ? (sunday - dayOfWeek) : 1;
                $scope.leave_request.return_date = moment(newValue).add(add, 'days');
                $scope.returnDateOptions.minDate = moment(newValue).add(1, 'days').toDate();

                // TODO: enable selecting a few days from the next month if the leave ends on the last day of the month
            }
        });

        $scope.showReturnDatePicker = function () {
            $scope.returnDatePickerIsVisible = true;
            angular.element(".return-date").css("max-height", "300px");
        };

        $scope.hideReturnDatePicker = function () {
            $scope.returnDatePickerIsVisible = false;
        };

        $scope.getLeaveLength = function () {
            if (!$scope.leave_request.start_date || !$scope.leave_request.end_date) {
                return 0;
            }
            var startMoment = moment($scope.leave_request.start_date);
            var endMoment = moment($scope.leave_request.end_date);
            return moment.duration(endMoment.diff(startMoment)).add(moment.duration(1, 'day')).asDays();
        };

        $scope.getRemainingDays = function (type) {
            if (!type) {
                return 0;
            }
            var leaveSetting = $scope.leaveSettings.filter(function (setting) {return setting.type.id === type;})[0];
            var leaveLength = $scope.getLeaveLength();
            return leaveSetting.remaining_days - leaveLength;
        };

        $scope.submit = function () {

            var data = $scope.leave_request;
            data.intern = $scope.intern.id;
            data.month = $scope.month.year() * 12 + ($scope.month.month());
            data.start_date = moment(data.start_date).format('YYYY-MM-DD');
            data.end_date = moment(data.end_date).format('YYYY-MM-DD');
            data.return_date = moment(data.return_date).format('YYYY-MM-DD');

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

.controller("LeaveRequestCancelCtrl", ["$scope", "$routeParams", "$location", "InternshipMonth", "Leave", "LeaveCancelRequest",
    function ($scope, $routeParams, $location, InternshipMonth, Leave, LeaveCancelRequest) {
        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});
        $scope.leave = Leave.get({id: $routeParams.leave_id});

        $scope.submit = function () {

            var leaveCancelRequest = new LeaveCancelRequest({
                intern: $scope.month.intern,
                month: $scope.month.month,
                leave_request: $scope.leave.request.id
            });
            leaveCancelRequest.$save(function() {
                $location.path("/planner");
            }, function(error) {
                try {
                    // We expect some validation errors
                    for (var i = 0; i < error.data.non_field_errors.length; i++) {
                        toastr.warning(error.data.non_field_errors[i]);
                    }
                } catch (e) {
                    // If we can't find the validation messages, then probably the error is something else.
                    // Just display the status text
                    toastr.error(error.statusText);
                }

            });

        };
}]);