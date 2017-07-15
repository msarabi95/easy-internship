/**
 * Created by MSArabi on 12/4/16.
 */
angular.module("ei.staff.rotations", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.accounts.models",
                                     "ei.utils", "ngRoute", "ngResource", "ngSanitize", "ngAnimate",
                                     "datatables", "datatables.bootstrap", "ngHandsontable", "ngScrollbars",
                                     "ui.bootstrap", "ui.select", "ei.rotations.directives", "ei.months.directives"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/requests/:university/:page?/", {
            templateUrl: "static/partials/staff/rotations/rotation-request-list.html?v=0008",
            controller: "RotationRequestListCtrl"
        })
        .when("/memos/", {
            templateUrl: "static/partials/staff/rotations/forward-list.html?v=0001",
            controller: "ForwardListCtrl"
        })
        .when("/rotations/", {
            templateUrl: "static/partials/staff/rotations/master-rota.html",
            controller: "MasterRotaCtrl"
        })
        .when("/rotations/:department/:month_id/", {
            templateUrl: "static/partials/staff/rotations/monthly-list.html?rel=1500118799360",
            controller: "MonthlyListCtrl"
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

.controller("RotationRequestListCtrl", ["$scope", "$filter", "$routeParams", "AcceptanceList", "RotationRequest", "FreezeRequest", "FreezeCancelRequest",
    function ($scope, $filter, $routeParams, AcceptanceList, RotationRequest, FreezeRequest, FreezeCancelRequest) {

        $scope.university = $routeParams.university;
        console.log($scope.university);
        if ( ['ksauhs', 'agu', 'outside'].indexOf($scope.university) === -1 ) {
            throw "Incorrect university URL parameter passed.";
        }

        $scope.page = $routeParams.page;

        function momentizeMonth(requests) {
            angular.forEach(requests, function (request, index) {
                request.month = moment({year: Math.floor(request.month / 12), month: (request.month % 12)});
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

                $scope.acceptance_lists = AcceptanceList.query({university: $scope.university}, function (lists) {
                    updateFilters(lists);
                }, function (error) {
                    toastr.error(error.statusText);
                });
                break;
            case 'kamc-memo':
                $scope.requests = RotationRequest.kamc_memo({university: $scope.university}, momentizeMonth);
                break;
            case 'outside':
                $scope.requests = RotationRequest.non_kamc({university: $scope.university}, momentizeMonth);
                break;
            case 'cancellation':
                $scope.requests = RotationRequest.cancellation({university: $scope.university}, momentizeMonth);
                break;
            case 'freezes':
                $scope.requests = FreezeRequest.open({university: $scope.university}, momentizeMonth);
                break;
            case 'freezecancels':
                $scope.requests = FreezeCancelRequest.open({university: $scope.university}, momentizeMonth);
        }

        $scope.reverseOptions = [
            {label: "Ascending", value: false},
            {label: "Descending", value: true}
        ];

        $scope.orderingOptions = [
            {label: "Submission date and time", value: function (request) {return request.submission_datetime.toDate();}},
            {label: "GPA", value: function (request) {return parseFloat(request.gpa)}},
            {label: "Name", value: function (request) {return request.intern_name;}},
            {label: "Hospital", value: function (request) {return request.requested_department_hospital_name;}}
        ];

        $scope.freezeOrderingOptions = [
            {label: "Submission date and time", value: function (request) {return request.submission_datetime.toDate();}},
            {label: "GPA", value: function (request) {return parseFloat(request.gpa)}},
            {label: "Name", value: function (request) {return request.intern_name;}}
        ];

        $scope.ordering = {
            option: $scope.page == 'freezes' || $scope.page == 'freezecancels' ? $scope.freezeOrderingOptions[0].value : $scope.orderingOptions[0].value,
            reverse: false
        };

        $scope.removeRequest = function (request) {
            var index = $scope.requests.indexOf(request);
            if (index > -1) {
                $scope.requests.splice(index, 1);
            }
        };

}])

.controller("ForwardListCtrl", ["$scope", "$compile", "$uibModal", "DTOptionsBuilder", "DTColumnBuilder", "Intern", "RotationRequest", "RotationRequestForward", function ($scope, $compile, $uibModal, DTOptionsBuilder, DTColumnBuilder, Intern, RotationRequest, RotationRequestForward) {
    var dtColumnsCommon = [
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
            })
    ];

    $scope.dtOptions1 = DTOptionsBuilder
        .fromFnPromise(function() {
            return RotationRequestForward.staff_memos_as_table().$promise;
        })
        .withOption("order", [[ 6, "asc" ]])
        .withOption("responsive", true)
        .withOption('fnRowCallback',
         function (nRow, aData, iDisplayIndex, iDisplayIndexFull) {
            $compile(nRow)($scope);
         })
        .withBootstrap();

    $scope.dtColumns1 = dtColumnsCommon.concat([
        DTColumnBuilder.newColumn(null).withTitle("Response").notSortable()
            .renderWith(function (data, type, full, meta) {
                return '<a class="btn btn-xs btn-primary" ng-click="openModal(' + data.rotation_request.id + ')"><i class="fa fa-pencil"></i> Record</a>';
            })
    ]);

    $scope.dtInstance1 = {};

    /* ******* */

    $scope.dtOptions2 = DTOptionsBuilder
        .fromFnPromise(function() {
            return RotationRequestForward.intern_memos_as_table().$promise;
        })
        .withOption("order", [[ 6, "asc" ]])
        .withOption("responsive", true)
        .withBootstrap();

    $scope.dtColumns2 = dtColumnsCommon.concat([
        DTColumnBuilder.newColumn(null).withTitle("Response").notSortable()
            .renderWith(function (data, type, full, meta) {
                return '<i>To be provided by intern</i>';
            })
    ]);

    $scope.dtInstance2 = {};

    /* ******* */

    $scope.dtOptions3 = DTOptionsBuilder
        .fromFnPromise(function() {
            return RotationRequestForward.memos_archive_as_table().$promise;
        })
        .withOption("order", [[ 6, "asc" ]])
        .withOption("responsive", true)
        .withBootstrap();

    $scope.dtColumns3 = dtColumnsCommon;

    $scope.dtInstance3 = {};

    var ResponseModalCtrl = ["$scope", "$uibModalInstance", "request", function ($scope, $uibModalInstance, request) {
        $scope.request = request;

        $scope.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        };

        $scope.ok = function () {
            $uibModalInstance.close($scope.response);
        }
    }];

    $scope.openModal = function (rotationRequestId) {
        var request = new RotationRequest({id: rotationRequestId});
        return $uibModal.open({
            animation: true,
            templateUrl: 'response-modal.html',
            controller: ResponseModalCtrl,
            resolve: {
                request: request
            }
        }).result.then(function (response) {
            request.$respond({is_approved: response.is_approved, comments: response.comment}, function () {
                $scope.dtInstance1.reloadData();
                $scope.dtInstance3.reloadData();
            }, function (error) {
                toastr.error(error);
            });
        });
    };
}])

.controller("MasterRotaCtrl", ["$scope", "$q", "Department", "Rotation", function ($scope, $q, Department, Rotation) {
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

            $scope.rotation_counts = Rotation.master_rota({year: newValue, hospital: 1});

            $scope.rotation_counts.$promise.then(function (rotationCounts) {
                var promises = [];
                for (var i = 0; i < rotationCounts.length; i++) {
                    var row = rotationCounts[i];
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
}])

.controller("MonthlyListCtrl", ["$scope", "$routeParams", "Batch", "Department", function ($scope, $routeParams, Batch, Department) {
    $scope.month = moment({year: Math.floor(parseInt($routeParams.month_id)/ 12), month: (parseInt($routeParams.month_id) % 12)});
    $scope.month_id = $routeParams.month_id;
    $scope.department = Department.get({id: $routeParams.department});

    $scope.batches = Batch.query(function (batches) {
        angular.forEach(batches, function (batch) {
            // Set default values for table display
            batch.ordering = '$index';
            batch.reverse = false;

            // Fetch info
            batch.monthly_list = Batch.monthly_list({
                id: batch.id,
                department: $routeParams.department,
                month: $routeParams.month_id
            });
            batch.monthly_list.$promise.then(function(rotations) {
                angular.forEach(rotations, function(rotation, index) {
                    rotation.request_datetime = moment(rotation.request_datetime);
                    rotation.approval_datetime = moment(rotation.approval_datetime);
                });
            });
        });
    });
}]);