/**
 * Created by MSArabi on 12/4/16.
 */
angular.module("ei.staff.rotations", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.accounts.models",
                                     "ei.utils", "ngRoute", "ngResource", "ngSanitize", "ngAnimate",
                                     "datatables", "datatables.bootstrap", "ngHandsontable", "ngScrollbars",
                                     "ui.bootstrap", "ui.select"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/requests/:page?/", {
            templateUrl: "static/partials/staff/rotations/rotation-request-list.html?v=0003",
            controller: "RotationRequestListCtrl"
        });

}])

.filter("filterByMonth", function() {
    return function (items, months) {
        if (!months || months.length == 0) {
            return items;
        }
        var filtered = [];
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            for (var j = 0; j < months.length; j++) {
                var month = months[j];
                if (item.month.isSame(month)) {
                    filtered.push(item);
                }
            }
        }
        return filtered;
    };
})
    
.filter("filterByDepartment", function() {
    return function (items, departments) {
        if (!departments || departments.length == 0) {
            return items;
        }
        var filtered = [];
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            for (var j = 0; j < departments.length; j++) {
                var department = departments[j];
                if (item.department.id == department.id) {
                    filtered.push(item);
                }
            }
        }
        return filtered;
    };
})

.controller("RotationRequestListCtrl", ["$scope", "$filter", "$q", "$routeParams", "$location", "$timeout", "loadWithRelated", "AcceptanceList", "Department", "AcceptanceSettings", "Internship", "InternshipMonth", "Intern", "Profile", "RotationRequest", "RequestedDepartment", "Specialty", "Hospital",
    function ($scope, $filter, $q, $routeParams, $location, $timeout, loadWithRelated, AcceptanceList, Department, AcceptanceSettings, Internship, InternshipMonth, Intern, Profile, RotationRequest, RequestedDepartment, Specialty, Hospital) {

        $scope.page = $routeParams.page;

        function loadRequestInfo(requests) {
            angular.forEach(requests, function (request, index) {
                request.month = InternshipMonth.get_by_internship_and_id({month_id: request.month, internship_id: request.internship});
                request.requested_department = loadWithRelated(request.requested_department, RequestedDepartment, [
                    [{department: Department}, [
                        {hospital: Hospital}
                    ]]
                ], true);
                request.specialty = Specialty.get({id: request.specialty});
                request.internship = loadWithRelated(request.internship, Internship, [
                    [{intern: Intern}, [
                        {profile: Profile}
                    ]]
                ], true);
                request.$promise = $q.all([
                    request.month.$promise,
                    request.requested_department.$promise,
                    request.specialty.$promise,
                    request.internship.$promise
                ])
            });
        }

        function updateFilters(acceptance_lists) {
            $scope.selected = $scope.selected || {};

            var filterMonths = [];
            var filterDepartments = [];

            for (var i = 0; i < acceptance_lists.length; i++) {
                var list = acceptance_lists[i];
                if (filterMonths.indexOf(list.month) == -1) {
                    filterMonths.push(list.month);
                }
                if ($filter('filter')(filterDepartments, {id: list.department.id}).length == 0) {
                    filterDepartments.push(list.department);
                }
            }
            $scope.filterMonths = filterMonths;
            $scope.filterDepartments = filterDepartments;
        }

        switch ($scope.page) {
            case 'kamc-nomemo':
                $scope.removeFromList = function (acceptanceList) {
                    var idx = $scope.acceptance_lists.indexOf(acceptanceList);
                    $scope.acceptance_lists.splice(idx, 1);
                    updateFilters($scope.acceptance_lists);
                };

                $scope.acceptance_lists = AcceptanceList.query(function (lists) {
                    updateFilters(lists);
                }, function (error) {
                    toastr.error(error.statusText);
                });
                //$scope.requests = RotationRequest.kamc_no_memo(loadRequestInfo);
                break;
            case 'kamc-memo':
                $scope.requests = RotationRequest.kamc_memo(loadRequestInfo);
                break;
            case 'outside':
                $scope.requests = RotationRequest.non_kamc(loadRequestInfo);
                break;
            case 'cancellation':
                $scope.requests = RotationRequest.cancellation(loadRequestInfo);
                break;
        }

        $scope.reverseOptions = [
            {label: "Ascending", value: false},
            {label: "Descending", value: true}
        ];

        $scope.orderingOptions = [
            {label: "Submission date and time", value: function (request) {return request.submission_datetime.toDate();}},
            {label: "GPA", value: function (request) {return parseFloat(request.internship.intern.gpa)}},
            {label: "Name", value: function (request) {return request.internship.intern.profile.en_full_name;}}
        ];
        $scope.ordering = {
            option: $scope.orderingOptions[0].value,
            reverse: false
        };

        $scope.removeRequest = function (request) {
            var index = $scope.requests.indexOf(request);
            if (index > -1) {
                $scope.requests.splice(index, 1);
            }
        };

        /* =============== */

    //$scope.monthFilter = function (selection) {
    //    // return a filter predicate function that filters months using the typed search value
    //    return function (value, index, array) {
    //        var monthLabel = $scope.monthLabels[value % $scope.selected.year];
    //        return monthLabel.toLowerCase().indexOf(selection.toLowerCase()) !== -1;
    //    }
    //};
    //
    //$scope.$watch("selected.year", function (newValue, oldValue) {
    //    if (newValue !== oldValue) {
    //        $scope.months = Array.apply(null, Array(12)).map(function (_, i) {return (newValue * 12) + i;});
    //    }
    //});
    //
    //$scope.$watchGroup(["selected.month", "selected.department"], function (newValue, oldValue) {
    //    if (newValue !== oldValue) {
    //        if (!!$scope.selected.month && !!$scope.selected.department) {
    //            $location.path("requests/" + $scope.selected.department.id + "/" + $scope.selected.month + "/")
    //        }
    //    }
    //});
    //
    //$scope.departments = Department.query();
    //$scope.departments.$promise.then(function (departments) {
    //    if (!!$routeParams.month_id && !!$routeParams.department_id) {
    //        var month = parseInt($routeParams.month_id);
    //        $scope.selected = {
    //            year:  (month - (month % 12)) / 12,
    //            month: month,
    //            department: departments.find(function (department, index) {
    //                return department.id == parseInt($routeParams.department_id)
    //            })
    //        }
    //    } else {
    //        $scope.selected = {
    //            year: 2016
    //        };
    //    }
    //
    //    $scope.monthLabels = {
    //        0: "January",
    //        1: "February",
    //        2: "March",
    //        3: "April",
    //        4: "May",
    //        5: "June",
    //        6: "July",
    //        7: "August",
    //        8: "September",
    //        9: "October",
    //        10: "November",
    //        11: "December"
    //    };
    //    $scope.moment = moment;
    //
    //    if (!!$scope.selected && !!$scope.selected.month && !!$scope.selected.department) {
    //        $scope.setting = AcceptanceSettings.get({month_id: $scope.selected.month, department_id: $scope.selected.department.id});
    //        $scope.setting.$promise.then(function (setting) {
    //            $scope.setting.criterionDescription = {FCFS: "submission date and time", GPA: "GPA"}[setting.criterion];
    //
    //            var $setting = setting,
    //                $department = $scope.selected.department,
    //                $month = $scope.selected.month;
    //
    //            if ($setting.total_seats == null) {
    //
    //                // Uncontrolled submission
    //                $scope.template = 'static/partials/staff/rotations/rotation-request-list-components/uncontrolled-request-list.html?v=0002';
    //                $scope.requests = RotationRequest.query_by_department_and_month({department_id: $department.id, month_id: $month});
    //                $scope.requests.$promise.then(function (requests) {
    //                    angular.forEach(requests, function (request, index) {
    //                        getFullRequestInfo(request, index);
    //                    });
    //                });
    //
    //                $scope.reverseOptions = [
    //                    {label: "Ascending", value: false},
    //                    {label: "Descending", value: true}
    //                ];
    //
    //                $scope.orderingOptions = [
    //                    {label: "Submission date and time", value: function (request) {return request.submission_datetime.toDate();}},
    //                    {label: "GPA", value: function (request) {return parseFloat(request.internship.intern.gpa)}},
    //                    {label: "Name", value: function (request) {return request.internship.intern.profile.en_full_name;}}
    //                ];
    //                $scope.ordering = {
    //                    option: $scope.orderingOptions[0].value,
    //                    reverse: false
    //                };
    //
    //                $scope.flag = function (flagName) {
    //                    $scope.flags = {};  // reset all flags
    //                    $scope.flags[flagName] = true;
    //
    //                    $timeout(function () {try {$scope.flags[flagName] = false;} catch(e) {/* Do nothing */}},  5000);
    //                };
    //
    //                $scope.respond = function (request, response, comments) {
    //                    request.$respond({is_approved: response, comments: comments}, function (data) {
    //                        // Move request to *closed* requests
    //                        var index = $scope.requests.indexOf(request);  // WARNING: indexOf not supported in all browsers (IE7 & 8)
    //                        $scope.requests.splice(index, 1);
    //                    }, function (error) {
    //                        toastr.error(error);
    //                    });
    //                };
    //
    //                $scope.forward = function (request) {
    //                    request.$forward({}, function (data) {
    //                        // Move request to *forwarded* requests
    //                        var index = $scope.internship.unreviewed_rotation_requests.indexOf(request);  // WARNING: indexOf not supported in all browsers (IE7 & 8)
    //                        $scope.internship.unreviewed_rotation_requests.splice(index, 1);
    //
    //                        $scope.internship.forwarded_unreviewed_rotation_requests.push(request);
    //                    }, function (error) {
    //                        toastr.error(error);
    //                    });
    //                };
    //
    //            } else if ($setting.criterion == 'FCFS' && $setting.can_submit_requests == false && moment().isBefore($setting.start_or_end_date)) {
    //
    //                // Controlled submission, criterion is FCFS, and no requests have been received yet (start date is yet to come)
    //                $scope.template = 'static/partials/staff/rotations/rotation-request-list-components/empty-request-list.html';
    //
    //                $scope.message = "Request submission for this department during this month will open on " + $setting.start_or_end_date.format("d MMM YYYY, hh:mm a") + "." ;
    //
    //            } else if ( ($setting.criterion == 'FCFS' && $setting.can_submit_requests == false && $setting.unoccupied_seats == 0)
    //                || ($setting.criterion == 'GPA' && $setting.can_submit_requests == true)) {
    //
    //                // Controlled submission, either criterion is FCFS & seats are all done, or criterion is GPA & submission isn't over yet
    //                // In both cases show a list of "disabled" requests
    //                $scope.template = 'static/partials/staff/rotations/rotation-request-list-components/disabled-request-list.html?v=0002';
    //                $scope.requests = RotationRequest.query_by_department_and_month({department_id: $department.id, month_id: $month});
    //                $scope.requests.$promise.then(function (requests) {
    //                    angular.forEach(requests, function (request, index) {
    //                        getFullRequestInfo(request, index);
    //                    });
    //                });
    //
    //                $scope.reverseOptions = [
    //                    {label: "Ascending", value: false},
    //                    {label: "Descending", value: true}
    //                ];
    //
    //                $scope.orderingOptions = [
    //                    {label: "Submission date and time", value: function (request) {return request.submission_datetime.toDate();}},
    //                    {label: "GPA", value: function (request) {return parseFloat(request.internship.intern.gpa)}},
    //                    {label: "Name", value: function (request) {return request.internship.intern.profile.en_full_name;}}
    //                ];
    //                $scope.ordering = {
    //                    option: $scope.orderingOptions[0].value,
    //                    reverse: false
    //                };
    //
    //                if ($setting.criterion == 'GPA') {
    //                    $scope.message = "Request submission is still ongoing. You'll be able to review submitted requests starting on " + $setting.start_or_end_date.format("d MMM YYYY, hh:mm a") + "." ;
    //                } else if ($setting.criterion == 'FCFS') {
    //                    $scope.message = "No more requests can be reviewed, as there are no longer any unoccupied seats.";
    //                }
    //
    //            } else {
    //
    //                // Controlled submission, either criterion is FCFS & submission has started but available seats aren't over
    //                // Or criterion is GPA, and submission is done
    //
    //                // TODO: ability to override automated recommendation
    //
    //                $scope.template = 'static/partials/staff/rotations/rotation-request-list-components/recommended-request-list.html?v=0002';
    //                $scope.requests = RotationRequest.query_by_department_and_month({department_id: $department.id, month_id: $month});
    //                $scope.requests.$promise.then(function (requests) {
    //                    var promises = [];
    //                    angular.forEach(requests, function (request, index) {
    //                        promises.push(getFullRequestInfo(request, index));
    //                    });
    //
    //                    $q.all(promises).then(function (p) {
    //                        // Make recommendation for accepted and declined requests
    //
    //                        // First, sort requests based on the acceptance criterion
    //                        var ordering = {};
    //                        if ($setting.criterion == 'GPA') {
    //                            ordering.option = function (request) {return parseFloat(request.internship.intern.gpa);};
    //                            ordering.reverse = true;
    //                        } else if ($setting.criterion == 'FCFS') {
    //                            ordering.option = function (request) {return request.submission_datetime.toDate();};
    //                            ordering.reverse = false;
    //                        }
    //                        var sortedRequests = $filter('orderBy')($scope.requests, ordering.option, ordering.reverse);
    //
    //                        // Second,
    //                        if ($setting.unoccupied_seats >= $scope.requests.length) {
    //                            // if the number of unoccupied seats is more than or equal to the number of
    //                            // requests, then everybody should be accepted
    //                            $scope.requests_to_be_approved = sortedRequests;
    //                            $scope.requests_to_be_declined = null;
    //                        } else {
    //                            // if not, select the first 'x' requests, where x = # of unoccupied seats
    //                            // these requests are the ones to be accepted
    //                            // the remaining requests are the ones to be declined
    //                            $scope.requests_to_be_approved = sortedRequests.slice(0, $setting.unoccupied_seats);
    //                            $scope.requests_to_be_declined = sortedRequests.slice($setting.unoccupied_seats);
    //
    //                        }
    //
    //                        $scope.addComment = function (array, index) {
    //                            $scope['requests_to_be_' + array][index].showComments = true;
    //                        };
    //
    //                        $scope.removeComment = function (array, index) {
    //                            $scope['requests_to_be_' + array][index].showComments = false;
    //                            $scope['requests_to_be_' + array][index].comments = null;
    //                        };
    //
    //                        $scope.confirm = function () {
    //                            var promises = [];
    //                            angular.forEach($scope.requests_to_be_approved, function (request, index) {
    //                                promises.push(RotationRequest.respond({is_approved: 1, comments: request.comments || "", suppress_message: true}, request));
    //                            });
    //                            angular.forEach($scope.requests_to_be_declined, function (request, index) {
    //                                promises.push(RotationRequest.respond({is_approved: 0, comments: request.comments || "", suppress_message: true}, request));
    //                            });
    //                            $q.all(promises).then(function () {
    //                                toastr.success("All responses recorded.");
    //
    //                                $scope.setting = AcceptanceSettings.get({department_id: $scope.selected.department.id, month_id: $scope.selected.month});
    //
    //                                $scope.requests_to_be_approved = null;
    //                                $scope.requests_to_be_declined = null;
    //                                $scope.requests = [];
    //
    //                            }, function (error) {
    //                                toastr.error(error);
    //                            });
    //                        }
    //                    });
    //
    //                });
    //
    //            }
    //
    //            function getFullRequestInfo(request, index) {
    //                $scope.requests[index].month = InternshipMonth.get_by_internship_and_id({internship_id: request.internship, month_id: request.month});
    //                $scope.requests[index].specialty = Specialty.get({id: request.specialty});
    //
    //                $scope.requests[index].internship = Internship.get({id: request.internship});
    //                $scope.requests[index].internship.$promise.then(function (internship) {
    //                    $scope.requests[index].internship.intern = Intern.get({id: internship.intern});
    //                    $scope.requests[index].internship.intern.$promise.then(function (intern) {
    //                        $scope.requests[index].internship.intern.profile = Profile.get({id: intern.profile})
    //                    });
    //                });
    //                $scope.requests[index].requested_department = RequestedDepartment.get({id: request.requested_department});
    //                $scope.requests[index].requested_department.$promise.then(function (requested_department) {
    //                    $scope.requests[index].requested_department.department = Department.get({id: requested_department.department});
    //                    $scope.requests[index].requested_department.department.$promise.then(function (department) {
    //                        $scope.requests[index].requested_department.department.specialty = Specialty.get({id: department.specialty});
    //                        $scope.requests[index].requested_department.department.hospital = Hospital.get({id: department.hospital});
    //                    })
    //                });
    //                return $q.all([
    //                    $scope.requests[index].month.$promise,
    //                    $scope.requests[index].specialty.$promise,
    //                    $scope.requests[index].internship.$promise,
    //                    $scope.requests[index].requested_department.$promise
    //                ])
    //            }
    //        });
    //    } else {
    //        $scope.template = null;
    //    }
    //});

}]);