/**
 * Created by MSArabi on 11/27/16.
 */
angular.module("ei.hospitals", ["ngRoute", "ei.hospitals.models", "ui.bootstrap"])

.config(["$routeProvider", function ($routeProvider) {
    $routeProvider
        .when("/seats/", {
            templateUrl: "static/partials/intern/hospitals/seat-setting-list.html?v=0001",
            controller: "SeatSettingListCtrl"
        })

}])

.controller("SeatSettingListCtrl", ["$scope", "$q", "Department", "DepartmentMonthSettings", "SeatSettings",
    function ($scope, $q, Department, DepartmentMonthSettings, SeatSettings) {
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

        $scope.$watch("displayYear", function (newValue, oldValue) {
            $scope.startMonth = newValue * 12;
            $scope.months = Array.apply(null, Array(12)).map(function (_, i) {return $scope.startMonth + i;});

            $scope.settings = SeatSettings.as_table({year: newValue, hospital: 1});
            $scope.settings.$promise.then(function (settingsTable) {
                var promises = [];
                for (var i = 0; i < settingsTable.length; i++) {
                    var row = settingsTable[i];
                    var first = row[0];

                    first.department = Department.get({id: first.department});
                    promises.push(first.department.$promise);
                }
                return $q.all(promises);
            });
        });

        $scope.displayYear = moment().year();

        $scope.loadNextYear = function () {
            $scope.displayYear += 1;
        };

        $scope.loadPreviousYear = function () {
            $scope.displayYear -= 1;
        };
}]);