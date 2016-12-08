/**
 * Created by MSArabi on 12/4/16.
 */
angular.module("ei.staff.hospitals", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.accounts.models",
                                     "ei.utils", "ngRoute", "ngResource", "ngSanitize",
                                     "datatables", "datatables.bootstrap", "ngHandsontable", "ngScrollbars",
                                     "ui.bootstrap", "ui.select"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/seats/", {
            templateUrl: "static/partials/staff/hospitals/acceptance-setting-list.html",
            controller: "AcceptanceSettingsListCtrl"
        });

}])

.controller("AcceptanceSettingsListCtrl", ["$scope", "hotRegisterer", "$uibModal", "Department", "GlobalSettings", "MonthSettings", "DepartmentSettings", "DepartmentMonthSettings",
    function ($scope, hotRegisterer, $uibModal, Department, GlobalSettings, MonthSettings, DepartmentSettings, DepartmentMonthSettings) {

    $scope.scrollbarsConfig = {
        theme: 'dark'
    };

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

    $scope.$watch('displayYear', function (newValue, oldValue) {
        $scope.startMonth = newValue * 12;

        // Make data

        $scope.months = Array.apply(null, Array(12)).map(function (_, i) {return $scope.startMonth + i;});
        $scope.data = $scope.departments.map(function (_, i) {return {department: _, name: _.name}});

        // Configure the table

        var hot = hotRegisterer.getInstance('seat-availabilities');

        var columns = [{data: 'name'}];
        for (var i = 0; i < $scope.months.length; i++) {
            var monthId = $scope.months[i];
            columns.push({
                data: dmSettingByDepartmentAndMonth(monthId)
            })
        }
        var schema = {name: null, id: null};

        hot.updateSettings({
            width: 1000,
            height: 200,
            dataSchema: schema,
            columns: columns,
            data: $scope.data,
            colHeaders: function (index) {return index == 0 ? "Department" : ($scope.monthLabels[index - 1])}
        });

        // The Joker function :)
        // Handles reading & writing data between the table and ngResource

        function dmSettingByDepartmentAndMonth(monthId) {
            return function (row, value) {

                // Retrieve the `DepartmentMonthSettings` record if it's present
                var department = row.department;
                var dmSetting = $scope.dmSettings.find(function (obj, index) {
                    return obj.department == department.id && obj.month == monthId;
                });

                if (typeof value == 'undefined') {  // No value passed, just return the total seats
                    if (typeof dmSetting !== 'undefined') {
                       return dmSetting.total_seats;
                    }
                } else { // SET
                    if (typeof dmSetting !== 'undefined') {
                        if (value == '') {
                            // Delete record if cell set to empty value
                            var index = $scope.dmSettings.indexOf(dmSetting);
                            dmSetting.$delete();
                            $scope.dmSettings.splice(index, 1);
                        } else {
                            // Make sure new value is actually different
                            if (parseInt(value) !== parseInt(dmSetting.total_seats)) {
                                dmSetting.total_seats = value;
                                dmSetting.$update(); // Should saving be done here or in the `AfterChange` event callback?
                            }
                        }
                    } else if (value !== '') {
                        dmSetting = new DepartmentMonthSettings({
                            department: department.id,
                            month: monthId,
                            total_seats: value
                        });
                        $scope.dmSettings.push(dmSetting);
                        dmSetting.$save(); // Should saving be done here or in the `AfterChange` event callback?
                    }
                }
            }
        }


    });

    // Load department and seat data and initiate table by displaying current year

    $scope.departments = Department.query(function (departments) {
        $scope.mSettings = MonthSettings.query();
        $scope.dSettings = DepartmentSettings.query();

        $scope.dmSettings = DepartmentMonthSettings.query(function (dmSettings) {
            $scope.displayYear = new Date().getFullYear(); // Show current year
        });
    });

    // Load global settings, and set watchers
    $scope.global = {};
    GlobalSettings.get_acceptance_criterion(function (data) {
        $scope.global.acceptance_criterion = data.acceptance_criterion;

        $scope.$watch('global.acceptance_criterion', function (newValue, oldValue) {
            GlobalSettings.set_acceptance_criterion({}, {'acceptance_criterion': newValue});
        });
    });
    GlobalSettings.get_acceptance_start_date_interval(function (data) {
        $scope.global.acceptance_start_date_interval = data.acceptance_start_date_interval;

        $scope.$watch('global.acceptance_start_date_interval', function (newValue, oldValue) {
            GlobalSettings.set_acceptance_start_date_interval({}, {'acceptance_start_date_interval': newValue});
        });
    });
    GlobalSettings.get_acceptance_end_date_interval(function (data) {
        $scope.global.acceptance_end_date_interval = data.acceptance_end_date_interval;

        $scope.$watch('global.acceptance_end_date_interval', function (newValue, oldValue) {
            GlobalSettings.set_acceptance_end_date_interval({}, {'acceptance_end_date_interval': newValue});
        });
    });

    $scope.getMomentFromMonthId = function (monthId) {
        return moment({year: Math.floor(monthId / 12), month: (monthId % 12)});
    };

    $scope.getSettingType = function (department, month) {
        var dmSetting = $scope.dmSettings.find(function (obj, index) {
            return obj.department == department.id && obj.month == month;
        }),
            dSetting = $scope.dSettings.find(function (obj, index) {
            return obj.department == department.id;
        }),
            mSetting = $scope.mSettings.find(function (obj, index) {
            return obj.month == month;
        });

        if (typeof dmSetting !== 'undefined' && dmSetting.acceptance_criterion) {
            return "DM";
        } else if (typeof dSetting !== 'undefined') {
            return "D";
        } else if (typeof mSetting !== 'undefined') {
            return "M";
        } else {
            return "G";
        }
    };

    $scope.getSetting = function (department, month) {
        var dmSetting = $scope.dmSettings.find(function (obj, index) {
            return obj.department == department.id && obj.month == month;
        }),
            dSetting = $scope.dSettings.find(function (obj, index) {
            return obj.department == department.id;
        }),
            mSetting = $scope.mSettings.find(function (obj, index) {
            return obj.month == month;
        });

        if (typeof dmSetting !== 'undefined' && dmSetting.acceptance_criterion) {
            return dmSetting;
        } else if (typeof dSetting !== 'undefined') {
            return dSetting;
        } else if (typeof mSetting !== 'undefined') {
            return mSetting;
        } else {
            return $scope.global;
        }
    };

    $scope.getMonthSetting = function (month) {
        return $scope.mSettings.find(function (obj, index) {
            return obj.month == month;
        })
    };

    $scope.getDepartmentSetting = function (department) {
        return $scope.dSettings.find(function (obj, index) {
            return obj.department == department.id;
        });
    };

    $scope.getDepartmentMonthSetting = function (department, month) {
        return $scope.dmSettings.find(function (obj, index) {
            return obj.department == department.id && obj.month == month;
        });
    };

    $scope.getAcceptanceCriterion = function (department, month) {
        return $scope.getSetting(department, month).acceptance_criterion;
    };

    $scope.getAcceptanceStartDate = function (department, month) {
        var setting = $scope.getSetting(department, month);
        var settingType = $scope.getSettingType(department, month);

        if (settingType == 'G' || settingType == 'D') {
            var momentMonth = $scope.getMomentFromMonthId(month);
            return momentMonth.subtract(setting.acceptance_start_date_interval, 'days').format("D MMM");
        } else if (settingType == 'DM' || settingType == 'M') {
            return moment(setting.acceptance_start_date).format("D MMM");
        }
    };

    $scope.getAcceptanceEndDate = function (department, month) {
        var setting = $scope.getSetting(department, month);
        var settingType = $scope.getSettingType(department, month);

        if (settingType == 'G' || settingType == 'D') {
            var momentMonth = $scope.getMomentFromMonthId(month);
            return momentMonth.subtract(setting.acceptance_end_date_interval, 'days').format("D MMM");
        } else if (settingType == 'DM' || settingType == 'M') {
            return moment(setting.acceptance_end_date).format("D MMM");
        }
    };

    $scope.getAcceptanceCriterionIcon = function (department, month) {
        switch ($scope.getAcceptanceCriterion(department, month)) {
            case "FCFS":
                return "fa-clock-o";
            case "GPA":
                return "fa-bar-chart";
            default:
                return "fa-close";
        }
    };

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

    $scope.getBadgeColor = function (department, month) {
        switch ($scope.getSettingType(department, month)) {
            case "DM":
                return 'red';
            case "D":
                return 'yellow';
            case "M":
                return 'green';
            default:
                return 'gray';
        }
    };

    $scope.openModal = function (department, month, size) {
        var modalInstance = $uibModal.open({
            animation: true,
            //ariaLabelledBy: 'modal-title',
            //ariaDescribedBy: 'modal-body',
            templateUrl: 'department-month-setting-modal.html',
            controller: 'DepartmentMonthSettingModalCtrl',
            size: size,
            resolve: {
                department: department,
                momentMonth: $scope.getMomentFromMonthId(month),
                dmSetting: $scope.getDepartmentMonthSetting(department, month)
            }
        });

        modalInstance.result.then(function (dmSetting) {
            if (dmSetting.id) {
                // Find index of the existing setting
                var index = $scope.dmSettings.indexOf($scope.getDepartmentMonthSetting(department, month));

                if (dmSetting.toDelete == true) {
                    $scope.dmSettings[index].$delete();
                    $scope.dmSettings.splice(index, 1);
                } else {
                    $scope.dmSettings[index] = dmSetting;
                    dmSetting.$update();
                }
            } else {
                dmSetting.department = department.id;
                dmSetting.month = month;
                DepartmentMonthSettings.save({}, dmSetting, function (saved) {
                    $scope.dmSettings.push(saved);
                });
            }
        });

    };

    $scope.openDModal = function (department, size) {
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: 'department-setting-modal.html',
            controller: 'DepartmentSettingModalCtrl',
            size: size,
            resolve: {
                department: department,
                dSetting: $scope.getDepartmentSetting(department)
            }
        });

        modalInstance.result.then(function (dSetting) {
            if (dSetting.id) {
                // Find index of the existing setting
                var index = $scope.dSettings.indexOf($scope.getDepartmentSetting(department));

                if (dSetting.toDelete == true) {
                    $scope.dSettings[index].$delete();
                    $scope.dSettings.splice(index, 1);
                } else {
                    $scope.dSettings[index] = dSetting;
                    dSetting.$update();
                }
            } else {
                dSetting.department = department.id;
                DepartmentSettings.save({}, dSetting, function (saved) {
                    $scope.dSettings.push(saved);
                });
            }
        });
    };

    $scope.openMModal = function (month, size) {
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: 'month-setting-modal.html',
            controller: 'MonthSettingModalCtrl',
            size: size,
            resolve: {
                momentMonth: $scope.getMomentFromMonthId(month),
                mSetting: $scope.getMonthSetting(month)
            }
        });

        modalInstance.result.then(function (mSetting) {
            if (mSetting.id) {
                // Find index of the existing setting
                var index = $scope.mSettings.indexOf($scope.getMonthSetting(month));

                if (mSetting.toDelete == true) {
                    $scope.mSettings[index].$delete();
                    $scope.mSettings.splice(index, 1);
                } else {
                    $scope.mSettings[index] = mSetting;
                    mSetting.$update();
                }
            } else {
                mSetting.month = month;
                MonthSettings.save({}, mSetting, function (saved) {
                    $scope.mSettings.push(saved);
                });
            }
        });

    };

    $scope.triggerHotTable = function () {
        $scope.showHotTable = !$scope.showHotTable;
        if ($scope.showHotTable == true) {
            var hot = hotRegisterer.getInstance('seat-availabilities');
            setTimeout(function () {
                hot.render();
            }, 100);
        }
    };

    $scope.loadNextYear = function () {
        $scope.displayYear += 1;
    };

    $scope.loadPreviousYear = function () {
        $scope.displayYear -= 1;
    };
}])

.controller("DepartmentMonthSettingModalCtrl", ["$scope", "$uibModalInstance", "department", "momentMonth", "dmSetting",
    function ($scope, $uibModalInstance, department, momentMonth, dmSetting) {
        // TODO: Isolate modal scope from route scope
        $scope.department = department;
        $scope.month = momentMonth;
        $scope.dmSetting = dmSetting;

        if (dmSetting) {
            $scope.dmSetting.acceptance_start_date_asDate = moment($scope.dmSetting.acceptance_start_date).toDate();
            $scope.dmSetting.acceptance_end_date_asDate = moment($scope.dmSetting.acceptance_end_date).toDate();
        }

        $scope.dpOptions = {
            showWeeks: false
        };

        $scope.ok = function () {
            $scope.dmSetting.acceptance_start_date = moment($scope.dmSetting.acceptance_start_date_asDate).format();
            $scope.dmSetting.acceptance_end_date = moment($scope.dmSetting.acceptance_end_date_asDate).format();

            if ($scope.dmSetting.total_seats == undefined && $scope.dmSetting.acceptance_criterion == "") {
                // If neither seat count or acceptance criterion is selected, then delete the dmSetting instance
                $scope.dmSetting.toDelete = true;
                $uibModalInstance.close($scope.dmSetting);
            } else {
                // Otherwise validate and submit form normally
                /* TODO: validate form before submitting
                 * 1- Seat count should be a number and should be present.
                 * 2- If criterion is selected, either start date or end date should be present.
                 */
                if ($scope.dmSetting.acceptance_criterion == 'FCFS' || $scope.dmSetting.acceptance_criterion == '') {
                    $scope.dmSetting.acceptance_end_date = null;
                }
                if ($scope.dmSetting.acceptance_criterion == 'GPA' || $scope.dmSetting.acceptance_criterion == '') {
                    $scope.dmSetting.acceptance_start_date = null;
                }
                $uibModalInstance.close($scope.dmSetting);
            }
        };

        $scope.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        };
}])

.controller("DepartmentSettingModalCtrl", ["$scope", "$uibModalInstance", "department", "dSetting",
    function ($scope, $uibModalInstance, department, dSetting) {
        // TODO: Isolate modal scope from route scope
        $scope.department = department;
        $scope.dSetting = dSetting;

        $scope.ok = function () {
            if ($scope.dSetting.acceptance_criterion == "") {
                // If no acceptance criterion is selected, then delete the dSetting instance
                $scope.dSetting.toDelete = true;
                $uibModalInstance.close($scope.dSetting);
            } else {
                // Otherwise validate and submit form normally
                /* TODO: validate form before submitting
                 * If criterion is selected, either start date or end date should be present.
                 */
                if ($scope.dSetting.acceptance_criterion == 'FCFS') {
                    $scope.dSetting.acceptance_end_date_interval = null;
                } else if ($scope.dSetting.acceptance_criterion == 'GPA') {
                    $scope.dSetting.acceptance_start_date_interval = null;
                }
                $uibModalInstance.close($scope.dSetting);
            }
        };

        $scope.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        };
}])

.controller("MonthSettingModalCtrl", ["$scope", "$uibModalInstance", "momentMonth", "mSetting",
    function ($scope, $uibModalInstance, momentMonth, mSetting) {
        // TODO: Isolate modal scope from route scope
        $scope.month = momentMonth;
        $scope.mSetting = mSetting;

        if (mSetting) {
            $scope.mSetting.acceptance_start_date_asDate = moment($scope.mSetting.acceptance_start_date).toDate();
            $scope.mSetting.acceptance_end_date_asDate = moment($scope.mSetting.acceptance_end_date).toDate();
        }

        $scope.dpOptions = {
            showWeeks: false
        };

        $scope.ok = function () {
            $scope.mSetting.acceptance_start_date = moment($scope.mSetting.acceptance_start_date_asDate).format();
            $scope.mSetting.acceptance_end_date = moment($scope.mSetting.acceptance_end_date_asDate).format();

            if ($scope.mSetting.acceptance_criterion == "") {
                // If no acceptance criterion is selected, then delete the mSetting instance
                $scope.mSetting.toDelete = true;
                $uibModalInstance.close($scope.mSetting);
            } else {
                // Otherwise validate and submit form normally
                /* TODO: validate form before submitting
                 * If criterion is selected, either start date or end date should be present.
                 */
                if ($scope.mSetting.acceptance_criterion == 'FCFS' || $scope.mSetting.acceptance_criterion == '') {
                    $scope.mSetting.acceptance_end_date = null;
                }
                if ($scope.mSetting.acceptance_criterion == 'GPA' || $scope.mSetting.acceptance_criterion == '') {
                    $scope.mSetting.acceptance_start_date = null;
                }
                $uibModalInstance.close($scope.mSetting);
            }
        };

        $scope.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        };
}]);