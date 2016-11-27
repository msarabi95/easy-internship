/**
 * Created by MSArabi on 11/27/16.
 */
angular.module("ei.hospitals", ["ngRoute", "ei.hospitals.models"])

.config(["$routeProvider", function ($routeProvider) {
    $routeProvider
        .when("/seats/", {
            templateUrl: "static/partials/intern/hospitals/acceptance-setting-list.html",
            controller: "AcceptanceSettingListCtrl"
        })

}])

.controller("AcceptanceSettingListCtrl", ["$scope", "Department", "DepartmentMonthSettings", "AcceptanceSettings",
    function ($scope, Department, DepartmentMonthSettings, AcceptanceSettings) {
        $scope.monthLabels = {
            0: "January",
            1: "February",
            2: "March",
            3: "April",
            4: "May",
            5: "June",
            6: "July",
            7: "August",
            8: "September",
            9: "October",
            10: "November",
            11: "December"
        };

        $scope.departments = Department.query();
        $scope.dmSettings = DepartmentMonthSettings.query();
        $scope.dmSettings.$promise.then(function (dmSettings) {
            $scope.settings = [];
            angular.forEach(dmSettings, function (item, index) {
                var setting = AcceptanceSettings.get({month_id: item.month, department_id: item.department});
                setting.$promise.then(function (setting) {
                    setting.department_id = item.department;
                    setting.month = item.month;
                    $scope.settings.push(setting);
                })
            });
        });

        $scope.$watch("displayYear", function (newValue, oldValue) {
            $scope.startMonth = newValue * 12;
            $scope.months = Array.apply(null, Array(12)).map(function (_, i) {return $scope.startMonth + i;});

        });

        $scope.getTotalSeats = function (department, month) {
            var dmSetting = $scope.dmSettings.find(function (obj, index) {
                return obj.department == department.id && obj.month == month;
            });

            if (dmSetting !== undefined) {
                return dmSetting.total_seats;
            } else {
                return "—";
            }
        };

        $scope.getMomentFromMonthId = function (monthId) {
            return moment({year: Math.floor(monthId / 12), month: (monthId % 12)});
        };

        $scope.getOccupiedSeats = function (department, month) {
            var setting = $scope.settings.find(function (obj, index) {
                return obj.department_id == department.id && obj.month == month;
            });
            if (setting !== undefined) {
                return setting.occupied_seats;
            } else {
                return "—";
            }
        };

        $scope.getUnoccupiedSeats = function (department, month) {
            var setting = $scope.settings.find(function (obj, index) {
                return obj.department_id == department.id && obj.month == month;
            });
            if (setting !== undefined) {
                return setting.unoccupied_seats;
            } else {
                return "—";
            }
        };

        $scope.getBookedSeats = function (department, month) {
            var setting = $scope.settings.find(function (obj, index) {
                return obj.department_id == department.id && obj.month == month;
            });
            if (setting !== undefined) {
                return setting.booked_seats;
            } else {
                return "—";
            }
        };

        $scope.loadNextYear = function () {
            $scope.displayYear += 1;
        };

        $scope.loadPreviousYear = function () {
            $scope.displayYear -= 1;
        };

        $scope.displayYear = 2016;
}]);