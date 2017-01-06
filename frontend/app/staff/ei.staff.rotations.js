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
            templateUrl: "static/partials/staff/rotations/rotation-request-list.html?v=0005",
            controller: "RotationRequestListCtrl"
        })
        .when("/memos/", {
            templateUrl: "static/partials/staff/rotations/forward-list.html",
            controller: "ForwardListCtrl"
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

}])

.controller("ForwardListCtrl", ["$scope", "DTOptionsBuilder", "DTColumnBuilder", "Intern", "RotationRequestForward", function ($scope, DTOptionsBuilder, DTColumnBuilder, Intern, RotationRequestForward) {
    $scope.dtOptions = DTOptionsBuilder
        .fromFnPromise(function() {
            return Intern.as_table().$promise;
        })
        .withOption("order", [[ 1, "asc" ]])
        .withOption("responsive", true)
        .withBootstrap();

    $scope.dtOptions1 = DTOptionsBuilder
        .fromFnPromise(function() {
            return RotationRequestForward.intern_memos_as_table().$promise;
        })
        .withOption("order", [[ 6, "asc" ]])
        .withOption("responsive", true)
        .withBootstrap();

    $scope.dtColumns = [
        DTColumnBuilder.newColumn('rotation_request.id').withTitle('#'),
        DTColumnBuilder.newColumn('rotation_request.intern_name').withTitle('Intern name'),
        DTColumnBuilder.newColumn('rotation_request.month').withTitle('Month')
            .renderWith(function (data, type, full, meta) {
                var year = Math.floor(data/12);
                var month = data % 12;
                return moment({year: year, month: month}).format('MMMM YYYY');
            }),
        DTColumnBuilder.newColumn('rotation_request.requested_department_name').withTitle('Department'),
        DTColumnBuilder.newColumn('rotation_request.requested_department_hospital_name').withTitle('Hospital'),
        DTColumnBuilder.newColumn('rotation_request.submission_datetime').withTitle('Submitted')
            .renderWith(function (data, type, full, meta) {
                return moment(data).format('D/MMM/YYYY, hh:mm a');
            }),
        DTColumnBuilder.newColumn('forward_datetime').withTitle('Forwarded')
            .renderWith(function (data, type, full, meta) {
                return data.format('D/MMM/YYYY, hh:mm a');
            }),
        DTColumnBuilder.newColumn(null).withTitle("Memo").notSortable()
            .renderWith(function (data, type, full, meta) {
                return '<a href="' + data.memo_file + '" class="btn btn-xs btn-danger">As PDF</a>';
            }),
        DTColumnBuilder.newColumn(null).withTitle(null).notSortable()
            .renderWith(function (data, type, full, meta) {
                return '<a class="btn btn-default btn-flat" href="#/interns/">View details</a>';
            })
    ];
}]);