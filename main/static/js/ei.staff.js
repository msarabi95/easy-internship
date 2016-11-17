/**
 * Created by MSArabi on 7/14/16.
 */
var app = angular.module("easyInternship",
                         ["ei.planner.models", "ei.accounts.models", "ei.utils", "ngRoute", "ngResource", "ngSanitize",
                             "datatables", "datatables.bootstrap", "ngHandsontable", "ngScrollbars",
                             "ui.bootstrap", "ui.select"]);

app.config(["$httpProvider", "$routeProvider", "$resourceProvider",
    function ($httpProvider, $routeProvider, $resourceProvider) {

    // These settings enable Django to receive Angular requests properly.
    // Check:
    // http://django-angular.readthedocs.io/en/latest/integration.html#xmlhttprequest
    // http://django-angular.readthedocs.io/en/latest/csrf-protection.html#cross-site-request-forgery-protection
    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

    // Check for messages with each response
    $httpProvider.interceptors.push(function ($q, $rootScope) {
       return {
           'response': function (response) {
               if ( $rootScope.fetchingMessages != true ) {
                   $rootScope.fetchingMessages = true;
                   $rootScope.$broadcast("fetchMessages");
               }
               return response;
           },
           'responseError': function (rejection) {
               if ( $rootScope.fetchingMessages != true ) {
                   $rootScope.fetchingMessages = true;
                   $rootScope.$broadcast("fetchMessages");
               }
               return $q.reject(rejection);
           }
       };
    });

    $routeProvider
        .when("/", {
            // This redirects users from / to /#/
            redirectTo: "/"
        })
        .when("/planner/", {
            redirectTo: "/planner/recent/"
        })
        .when("/planner/recent/", {
            templateUrl: "partials/planner/staff/list-recent-requests.html",
            controller: "ListRecentRequestsCtrl"
        })
        .when("/planner/all/", {
            templateUrl: "partials/planner/staff/intern-list.html",
            controller: "InternListCtrl"
        })
        .when("/planner/:id/", {
            templateUrl: "partials/planner/staff/intern-detail.html",
            controller: "InternDetailCtrl"
        })
        .when("/seats/", {
            templateUrl: "partials/planner/staff/seat-availability-list.html",
            controller: "AcceptanceSettingsListCtrl"
        })
        .when("/requests/:department_id?/:month_id?/", {
            templateUrl: "partials/planner/staff/rotation-request-list.html",
            controller: "RotationRequestListCtrl"
        });

    $resourceProvider.defaults.stripTrailingSlashes = false;

}]);

app.run(function ($rootScope, $resource) {
    toastr.options.positionClass = "toast-top-center";
    $rootScope.$on("fetchMessages", getMessages);

    function getMessages(event, eventData) {
        var messages = $resource("messages").query(function (messages) {
            $rootScope.fetchingMessages = false;
            for (var i = 0; i < messages.length; i++) {
                toastr[messages[i].level_tag](messages[i].message);
            }
        });
    }

    $rootScope.fetchingMessages = true;
    getMessages("", {});
});

app.controller("MenuCtrl", ["$scope", "$route", "$location", function ($scope, $route, $location) {
    $scope.isActive = function (viewLocation) {
        return viewLocation == "#" + $location.path();
    }
}]);

app.controller("ListRecentRequestsCtrl", ["$scope", "Internship", "RotationRequest", "Intern", "Profile",
    function ($scope, Internship, RotationRequest, Intern, Profile) {
        $scope.internships = Internship.with_unreviewed_requests();

        $scope.internships.$promise.then(function (internships) {
            angular.forEach(internships, function (internship, index) {
                // Load the intern profile and standard profile
                $scope.internships[index].intern = Intern.get({id: internship.intern});
                $scope.internships[index].intern.$promise.then(function (intern) {
                    $scope.internships[index].intern.profile = Profile.get({id: intern.profile});
                });

                // Load rotation requests
                angular.forEach(internship.rotation_requests, function (request_id, request_id_index) {
                    $scope.internships[index].rotation_requests[request_id_index] = RotationRequest.get({id: request_id});
                });

            });
        });
}]);

app.controller("InternListCtrl", ["$scope", "DTOptionsBuilder", "DTColumnDefBuilder", "Internship", "Intern", "Profile",
    function ($scope, DTOptionsBuilder, DTColumnDefBuilder, Internship, Intern, Profile) {
        $scope.internships = Internship.query();

        $scope.internships.$promise.then(function (internships) {
            angular.forEach(internships, function (internship, index) {
                // Load the intern profile and standard profile
                $scope.internships[index].intern = Intern.get({id: internship.intern});
                $scope.internships[index].intern.$promise.then(function (intern) {
                    $scope.internships[index].intern.profile = Profile.get({id: intern.profile});
                });
            });
        });


        /* FIXME:
        * - Load datatable data from a dedicated endpoint.
        * - Display more info.
        * - Fix search and sorting issues.
        * */
        $scope.dtOptions = DTOptionsBuilder
            .fromSource()
            .withOption("order", [[ 2, "asc" ]])
            .withOption("responsive", true)
            .withBootstrap();

        $scope.dtColumns = [
            DTColumnDefBuilder.newColumnDef(0).notSortable(),
            DTColumnDefBuilder.newColumnDef([1, 2]).withOption("width", "20%"),
            DTColumnDefBuilder.newColumnDef(5).notSortable()
        ];
}]);

app.controller("InternDetailCtrl", ["$scope", "$routeParams", "$timeout", "Internship", "Intern", "Profile", "User", "InternshipMonth",
    "RotationRequest", "RequestedDepartment", "Specialty", "Department", "Hospital", "RotationRequestResponse", "RotationRequestForward",
    "RotationRequestForwardResponse", "Rotation",
    function ($scope, $routeParams, $timeout, Internship, Intern, Profile, User, InternshipMonth, RotationRequest, RequestedDepartment,
              Specialty, Department, Hospital, RotationRequestResponse, RotationRequestForward, RotationRequestForwardResponse, Rotation) {
        $scope.internship = Internship.get({id: $routeParams.id});

        $scope.internship.$promise.then(function (internship) {

            $scope.internship.intern = Intern.get({id: internship.intern});
            $scope.internship.intern.$promise.then(function (intern) {

                $scope.internship.intern.profile = Profile.get({id: intern.profile});
                $scope.internship.intern.profile.$promise.then(function (profile) {

                    $scope.internship.intern.profile.user = User.get({id: profile.user});
                })
            });

            angular.forEach($scope.internship.months, function (month_id, index) {
                $scope.internship.months[index] = InternshipMonth.get_by_internship_and_id({internship_id: internship.id, month_id: month_id});
                $scope.internship.months[index].$promise.then(function (internshipMonth) {

                    $scope.internship.months[index].occupied = (internshipMonth.current_rotation !== null);
                    $scope.internship.months[index].requested = (internshipMonth.current_request !== null);

                    if (internshipMonth.requested) {
                        $scope.internship.months[index].current_request = RotationRequest.get({id: internshipMonth.current_request});
                        $scope.internship.months[index].current_request.$promise.then(function (rotation_request) {

                            $scope.internship.months[index].current_request.specialty =
                                Specialty.get({id: rotation_request.specialty});

                            $scope.internship.months[index].current_request.requested_department =
                                RequestedDepartment.get({id: rotation_request.requested_department});
                            $scope.internship.months[index].current_request.requested_department.$promise.then(function (requested_department) {

                                $scope.internship.months[index].current_request.requested_department.department =
                                    Department.get({id: requested_department.department});
                                $scope.internship.months[index].current_request.requested_department.department.$promise.then(function (department) {

                                    $scope.internship.months[index].current_request.requested_department.department.hospital =
                                        Hospital.get({id: department.hospital});
                                })
                            });
                        });
                    }

                    if (internshipMonth.occupied) {
                        $scope.internship.months[index].current_rotation = Rotation.get({id: internshipMonth.current_rotation});
                        $scope.internship.months[index].current_rotation.$promise.then(function (rotation) {

                            $scope.internship.months[index].current_rotation.specialty = Specialty.get({id: rotation.specialty});

                            $scope.internship.months[index].current_rotation.department = Department.get({id: rotation.department});
                            $scope.internship.months[index].current_rotation.department.$promise.then(function (department) {

                                $scope.internship.months[index].current_rotation.department.hospital =
                                    Hospital.get({id: department.hospital});
                            })
                        })
                    }
                });
            });

            $scope.months = $scope.internship.months; // a handy shortcut

            // Load unreviewed and closed rotation requests separately
            angular.forEach($scope.internship.unreviewed_rotation_requests, function (id, index) {
                $scope.internship.unreviewed_rotation_requests[index] = RotationRequest.get({id: id});
                $scope.internship.unreviewed_rotation_requests[index].$promise.then(loadRotationRequestDetails(index, "unreviewed"));
            });

            angular.forEach($scope.internship.forwarded_unreviewed_rotation_requests, function (id, index) {
                $scope.internship.forwarded_unreviewed_rotation_requests[index] = RotationRequest.get({id: id});
                $scope.internship.forwarded_unreviewed_rotation_requests[index].$promise.then(loadRotationRequestDetails(index, "forwarded_unreviewed"));
            });

            angular.forEach($scope.internship.closed_rotation_requests, function (id, index) {
                $scope.internship.closed_rotation_requests[index] = RotationRequest.get({id: id});
                $scope.internship.closed_rotation_requests[index].$promise.then(loadRotationRequestDetails(index, "closed"));
            });

            // A common function to avoid repitition
            function loadRotationRequestDetails(index, type) {
                return function (request) {
                    $scope.internship[type + "_rotation_requests"][index].month =
                        InternshipMonth.get_by_internship_and_id({internship_id: internship.id, month_id: request.month});

                    $scope.internship[type + "_rotation_requests"][index].specialty =
                        Specialty.get({id: request.specialty});

                    $scope.internship[type + "_rotation_requests"][index].requested_department =
                        RequestedDepartment.get({id: request.requested_department});

                    $scope.internship[type + "_rotation_requests"][index].requested_department.$promise.then(function (requested_department) {
                        $scope.internship[type + "_rotation_requests"][index].requested_department.department =
                            Department.get({id: requested_department.department});

                        $scope.internship[type + "_rotation_requests"][index].requested_department.department.$promise.then(function (department) {
                            $scope.internship[type + "_rotation_requests"][index].requested_department.department.hospital =
                                Hospital.get({id: department.hospital});
                        })
                    });

                    if (!!request.response) {
                        $scope.internship[type + "_rotation_requests"][index].response =
                            RotationRequestResponse.get({id: request.response});
                    }

                    if (!!request.forward) {
                        $scope.internship[type + "_rotation_requests"][index].forward =
                            RotationRequestForward.get({id: request.forward});

                        $scope.internship[type + "_rotation_requests"][index].forward.$promise.then(function (forward) {
                            if (!!forward.response) {
                                $scope.internship[type + "_rotation_requests"][index].forward.response =
                                    RotationRequestForwardResponse.get({id: forward.response});
                            }
                        })
                    }
                };
            }
        });

        $scope.flag = function (flagName) {
            $scope.flags = {};  // reset all flags
            $scope.flags[flagName] = true;

            $timeout(function () {try {$scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
        };

        $scope.respond = function (request, response, comments) {
            request.$respond({is_approved: response, comments: comments}, function (data) {
                // Move request to *closed* requests
                var index = $scope.internship.unreviewed_rotation_requests.indexOf(request);  // WARNING: indexOf not supported in all browsers (IE7 & 8)
                $scope.internship.unreviewed_rotation_requests.splice(index, 1);
                $scope.internship.closed_rotation_requests.push(request);
            }, function (error) {
                toastr.error(error);
            });
        };

        $scope.forward = function (request) {
            request.$forward({}, function (data) {
                // Move request to *forwarded* requests
                var index = $scope.internship.unreviewed_rotation_requests.indexOf(request);  // WARNING: indexOf not supported in all browsers (IE7 & 8)
                $scope.internship.unreviewed_rotation_requests.splice(index, 1);

                $scope.internship.forwarded_unreviewed_rotation_requests.push(request);
            }, function (error) {
                toastr.error(error);
            });
        };

        $scope.getStatus = function (request) {
            if (!!request.response) {
                return request.response.is_approved ? "Approved" : "Declined";
            } else if (!!request.forward && !!request.forward.response) {
                return request.forward.response.is_approved ? "Approved" : "Declined";
            }
        };

        $scope.getClass = function (request) {
            var status = $scope.getStatus(request);
            if (status == "Approved") {
                return "success";
            } else {
                return "danger";
            }
        }
}]);

app.controller("AcceptanceSettingsListCtrl", ["$scope", "hotRegisterer", "$uibModal", "Department", "GlobalSettings", "MonthSettings", "DepartmentSettings", "DepartmentMonthSettings",
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
}]);

app.controller("DepartmentMonthSettingModalCtrl", ["$scope", "$uibModalInstance", "department", "momentMonth", "dmSetting",
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
}]);

app.controller("DepartmentSettingModalCtrl", ["$scope", "$uibModalInstance", "department", "dSetting",
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
}]);

app.controller("MonthSettingModalCtrl", ["$scope", "$uibModalInstance", "momentMonth", "mSetting",
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

app.controller("RotationRequestListCtrl", ["$scope", "$filter", "$q", "$routeParams", "$location", "$timeout", "Department", "AcceptanceSettings", "Internship", "InternshipMonth", "Intern", "Profile", "RotationRequest", "RequestedDepartment", "Specialty", "Hospital",
    function ($scope, $filter, $q, $routeParams, $location, $timeout, Department, AcceptanceSettings, Internship, InternshipMonth, Intern, Profile, RotationRequest, RequestedDepartment, Specialty, Hospital) {

    $scope.monthFilter = function (selection) {
        // return a filter predicate function that filters months using the typed search value
        return function (value, index, array) {
            var monthLabel = $scope.monthLabels[value % $scope.selected.year];
            return monthLabel.toLowerCase().indexOf(selection.toLowerCase()) !== -1;
        }
    };

    $scope.$watch("selected.year", function (newValue, oldValue) {
        if (newValue !== oldValue) {
            $scope.months = Array.apply(null, Array(12)).map(function (_, i) {return (newValue * 12) + i;});
        }
    });

    $scope.$watchGroup(["selected.month", "selected.department"], function (newValue, oldValue) {
        if (newValue !== oldValue) {
            if (!!$scope.selected.month && !!$scope.selected.department) {
                $location.path("requests/" + $scope.selected.department.id + "/" + $scope.selected.month + "/")
            }
        }
    });

    $scope.departments = Department.query();
    $scope.departments.$promise.then(function (departments) {
        if (!!$routeParams.month_id && !!$routeParams.department_id) {
            var month = parseInt($routeParams.month_id);
            $scope.selected = {
                year:  (month - (month % 12)) / 12,
                month: month,
                department: departments.find(function (department, index) {
                    return department.id == parseInt($routeParams.department_id)
                })
            }
        } else {
            $scope.selected = {
                year: 2016
            };
        }

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
        $scope.moment = moment;

        if (!!$scope.selected && !!$scope.selected.month && !!$scope.selected.department) {
            $scope.setting = AcceptanceSettings.get({month_id: $scope.selected.month, department_id: $scope.selected.department.id});
            $scope.setting.$promise.then(function (setting) {
                $scope.setting.criterionDescription = {FCFS: "submission date and time", GPA: "GPA"}[setting.criterion];

                var $setting = setting,
                    $department = $scope.selected.department,
                    $month = $scope.selected.month;

                if ($setting.total_seats == null) {

                    // Uncontrolled submission
                    $scope.template = 'partials/planner/staff/rotation-request-list-components/uncontrolled-request-list.html';
                    $scope.requests = RotationRequest.query_by_department_and_month({department_id: $department.id, month_id: $month});
                    $scope.requests.$promise.then(function (requests) {
                        angular.forEach(requests, function (request, index) {
                            getFullRequestInfo(request, index);
                        });
                    });

                    $scope.reverseOptions = [
                        {label: "Ascending", value: false},
                        {label: "Descending", value: true}
                    ];

                    $scope.orderingOptions = [
                        {label: "Submission date and time", value: function (request) {return moment(request.submission_datetime).toDate();}},
                        {label: "GPA", value: function (request) {return parseFloat(request.internship.intern.gpa)}},
                        {label: "Name", value: function (request) {return request.internship.intern.profile.en_full_name;}}
                    ];
                    $scope.ordering = {
                        option: $scope.orderingOptions[0].value,
                        reverse: false
                    };

                    $scope.flag = function (flagName) {
                        $scope.flags = {};  // reset all flags
                        $scope.flags[flagName] = true;

                        $timeout(function () {try {$scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
                    };

                    $scope.respond = function (request, response, comments) {
                        request.$respond({is_approved: response, comments: comments}, function (data) {
                            // Move request to *closed* requests
                            var index = $scope.requests.indexOf(request);  // WARNING: indexOf not supported in all browsers (IE7 & 8)
                            $scope.requests.splice(index, 1);
                        }, function (error) {
                            toastr.error(error);
                        });
                    };

                    $scope.forward = function (request) {
                        request.$forward({}, function (data) {
                            // Move request to *forwarded* requests
                            var index = $scope.internship.unreviewed_rotation_requests.indexOf(request);  // WARNING: indexOf not supported in all browsers (IE7 & 8)
                            $scope.internship.unreviewed_rotation_requests.splice(index, 1);

                            $scope.internship.forwarded_unreviewed_rotation_requests.push(request);
                        }, function (error) {
                            toastr.error(error);
                        });
                    };

                } else if ($setting.criterion == 'FCFS' && $setting.can_submit_requests == false && moment().isBefore(moment($setting.start_or_end_date))) {

                    // Controlled submission, criterion is FCFS, and no requests have been received yet (start date is yet to come)
                    $scope.template = 'partials/planner/staff/rotation-request-list-components/empty-request-list.html';

                    $scope.message = "Request submission for this department during this month will open on " + moment($setting.start_or_end_date).format("d MMM YYYY, hh:mm a") + "." ;

                } else if ( ($setting.criterion == 'FCFS' && $setting.can_submit_requests == false && $setting.unoccupied_seats == 0)
                    || ($setting.criterion == 'GPA' && $setting.can_submit_requests == true)) {

                    // Controlled submission, either criterion is FCFS & seats are all done, or criterion is GPA & submission isn't over yet
                    // In both cases show a list of "disabled" requests
                    $scope.template = 'partials/planner/staff/rotation-request-list-components/disabled-request-list.html';
                    $scope.requests = RotationRequest.query_by_department_and_month({department_id: $department.id, month_id: $month});
                    $scope.requests.$promise.then(function (requests) {
                        angular.forEach(requests, function (request, index) {
                            getFullRequestInfo(request, index);
                        });
                    });

                    $scope.reverseOptions = [
                        {label: "Ascending", value: false},
                        {label: "Descending", value: true}
                    ];

                    $scope.orderingOptions = [
                        {label: "Submission date and time", value: function (request) {return moment(request.submission_datetime).toDate();}},
                        {label: "GPA", value: function (request) {return parseFloat(request.internship.intern.gpa)}},
                        {label: "Name", value: function (request) {return request.internship.intern.profile.en_full_name;}}
                    ];
                    $scope.ordering = {
                        option: $scope.orderingOptions[0].value,
                        reverse: false
                    };

                    if ($setting.criterion == 'GPA') {
                        $scope.message = "Request submission is still ongoing. You'll be able to review submitted requests starting on " + moment($setting.start_or_end_date).format("d MMM YYYY, hh:mm a") + "." ;
                    } else if ($setting.criterion == 'FCFS') {
                        $scope.message = "No more requests can be reviewed, as there are no longer any unoccupied seats.";
                    }

                } else {

                    // Controlled submission, either criterion is FCFS & submission has started but available seats aren't over
                    // Or criterion is GPA, and submission is done

                    // TODO: ability to override automated recommendation

                    $scope.template = 'partials/planner/staff/rotation-request-list-components/recommended-request-list.html';
                    $scope.requests = RotationRequest.query_by_department_and_month({department_id: $department.id, month_id: $month});
                    $scope.requests.$promise.then(function (requests) {
                        var promises = [];
                        angular.forEach(requests, function (request, index) {
                            promises.push(getFullRequestInfo(request, index));
                        });

                        $q.all(promises).then(function (p) {
                            // Make recommendation for accepted and declined requests

                            // First, sort requests based on the acceptance criterion
                            var ordering = {};
                            if ($setting.criterion == 'GPA') {
                                ordering.option = function (request) {return parseFloat(request.internship.intern.gpa);};
                                ordering.reverse = true;
                            } else if ($setting.criterion == 'FCFS') {
                                ordering.option = function (request) {return moment(request.submission_datetime).toDate();};
                                ordering.reverse = false;
                            }
                            var sortedRequests = $filter('orderBy')($scope.requests, ordering.option, ordering.reverse);

                            // Second,
                            if ($setting.unoccupied_seats >= $scope.requests.length) {
                                // if the number of unoccupied seats is more than or equal to the number of
                                // requests, then everybody should be accepted
                                $scope.requests_to_be_approved = sortedRequests;
                                $scope.requests_to_be_declined = null;
                            } else {
                                // if not, select the first 'x' requests, where x = # of unoccupied seats
                                // these requests are the ones to be accepted
                                // the remaining requests are the ones to be declined
                                $scope.requests_to_be_approved = sortedRequests.slice(0, $setting.unoccupied_seats);
                                $scope.requests_to_be_declined = sortedRequests.slice($setting.unoccupied_seats);

                            }

                            $scope.addComment = function (array, index) {
                                $scope['requests_to_be_' + array][index].showComments = true;
                            };

                            $scope.removeComment = function (array, index) {
                                $scope['requests_to_be_' + array][index].showComments = false;
                                $scope['requests_to_be_' + array][index].comments = null;
                            };

                            $scope.confirm = function () {
                                var promises = [];
                                angular.forEach($scope.requests_to_be_approved, function (request, index) {
                                    promises.push(RotationRequest.respond({is_approved: 1, comments: request.comments || "", suppress_message: true}, request));
                                });
                                angular.forEach($scope.requests_to_be_declined, function (request, index) {
                                    promises.push(RotationRequest.respond({is_approved: 0, comments: request.comments || "", suppress_message: true}, request));
                                });
                                $q.all(promises).then(function () {
                                    toastr.success("All responses recorded.");

                                    $scope.setting = AcceptanceSettings.get({department_id: $scope.selected.department.id, month_id: $scope.selected.month});

                                    $scope.requests_to_be_approved = null;
                                    $scope.requests_to_be_declined = null;
                                    $scope.requests = [];

                                }, function (error) {
                                    toastr.error(error);
                                });
                            }
                        });

                    });

                }

                function getFullRequestInfo(request, index) {
                    $scope.requests[index].month = InternshipMonth.get_by_internship_and_id({internship_id: request.internship, month_id: request.month});
                    $scope.requests[index].specialty = Specialty.get({id: request.specialty});

                    $scope.requests[index].internship = Internship.get({id: request.internship});
                    $scope.requests[index].internship.$promise.then(function (internship) {
                        $scope.requests[index].internship.intern = Intern.get({id: internship.intern});
                        $scope.requests[index].internship.intern.$promise.then(function (intern) {
                            $scope.requests[index].internship.intern.profile = Profile.get({id: intern.profile})
                        });
                    });
                    $scope.requests[index].requested_department = RequestedDepartment.get({id: request.requested_department});
                    $scope.requests[index].requested_department.$promise.then(function (requested_department) {
                        $scope.requests[index].requested_department.department = Department.get({id: requested_department.department});
                        $scope.requests[index].requested_department.department.$promise.then(function (department) {
                            $scope.requests[index].requested_department.department.specialty = Specialty.get({id: department.specialty});
                            $scope.requests[index].requested_department.department.hospital = Hospital.get({id: department.hospital});
                        })
                    });
                    return $q.all([
                        $scope.requests[index].month.$promise,
                        $scope.requests[index].specialty.$promise,
                        $scope.requests[index].internship.$promise,
                        $scope.requests[index].requested_department.$promise
                    ])
                }
            });
        } else {
            $scope.template = null;
        }
    });

}]);