/**
 * Created by MSArabi on 12/4/16.
 */
angular.module("ei.staff.accounts", ["ei.months.models", "ei.accounts.models",
                                     "ei.utils", "ei.rotations.directives", "ei.months.directives",
                                     "ngRoute", "datatables", "datatables.bootstrap",
                                     "ui.bootstrap", "ui.select", "angularUtils.directives.dirPagination"])

.config(["$routeProvider", function ($routeProvider) {
    $routeProvider
        .when("/interns/", {
            templateUrl: "static/partials/staff/interns/intern-list.html?v=0001",
            controller: "InternListCtrl"
        })
        .when("/interns/summary/", {
            templateUrl: "static/partials/staff/interns/plans-summary.html?v=0007",
            controller: "PlansSummaryCtrl"
        })
        .when("/interns/:id/", {
            templateUrl: "static/partials/staff/interns/intern-detail.html?rel=1506235365795",
            controller: "InternDetailCtrl"
        });
}])

.controller("InternListCtrl", ["$scope", "$compile", "DTOptionsBuilder", "DTColumnBuilder", "DTColumnDefBuilder", "Batch", "Intern", "Profile",
    function ($scope, $compile, DTOptionsBuilder, DTColumnBuilder, DTColumnDefBuilder, Batch, Intern, Profile) {

        $scope.dtOptions = {};

        $scope.batches = Batch.query(function (batches) {

            angular.forEach(batches, function (batch) {
                $scope.dtOptions['batch_' + String(batch.id)] = DTOptionsBuilder
                    .fromFnPromise(function() {
                        return Batch.interns({id: batch.id}).$promise;
                    })
                    .withOption("order", [[ 1, "asc" ]])
                    .withOption("responsive", true)
                    .withBootstrap();
            });
        });


        $scope.dtColumns = [
            DTColumnBuilder.newColumn(null).withTitle(null).notSortable()
                .renderWith(function (data, type, full, meta) {
                    return '<img src="' + data.mugshot + '" class="img-circle img-bordered-sm img-sm"/>';
                }),
            DTColumnBuilder.newColumn('name').withTitle('Name'),
            DTColumnBuilder.newColumn('student_number').withTitle('Student Number'),
            DTColumnBuilder.newColumn('badge_number').withTitle('Badge Number'),
            DTColumnBuilder.newColumn('email').withTitle('Email'),
            DTColumnBuilder.newColumn('mobile_number').withTitle('Mobile Number'),
            DTColumnBuilder.newColumn(null).withTitle(null).notSortable()
                .renderWith(function (data, type, full, meta) {
                    return '<a class="btn btn-default btn-flat" href="#/interns/' + data.internship_id + '/">View details</a>';
                })
        ];
}])

.controller("InternDetailCtrl", ["$scope", "$routeParams", "Internship", function ($scope, $routeParams, Internship) {
    $scope.internship = Internship.get({id: $routeParams.id});

    $scope.internship.$promise.then(function (internship) {

        $scope.internship.unreviewed_rotation_requests = [];
        $scope.internship.forwarded_rotation_requests = [];
        $scope.internship.closed_rotation_requests = [];

        angular.forEach(internship.rotation_requests, function (rotation_request, index) {

            var year = Math.floor(rotation_request.month/12);
            var month = rotation_request.month % 12;
            rotation_request.month = moment({year: year, month: month, monthId: rotation_request.month});
            rotation_request.submission_datetime = moment(rotation_request.submission_datetime);

            if (!!rotation_request.response) {

                rotation_request.response.response_datetime = moment(rotation_request.response.response_datetime);
                $scope.internship.closed_rotation_requests.push(rotation_request);

            } else if (!!rotation_request.forward) {

                rotation_request.forward.forward_datetime = moment(rotation_request.forward.forward_datetime);
                $scope.internship.forwarded_rotation_requests.push(rotation_request);

            } else {

                $scope.internship.unreviewed_rotation_requests.push(rotation_request);

            }
        });
    });

    $scope.moveToPastRequests = function (request) {
        // Move request to *closed* requests
        var index = $scope.internship.unreviewed_rotation_requests.indexOf(request);  // WARNING: indexOf not supported in all browsers (IE7 & 8)
        if (index > -1) {
            $scope.internship.unreviewed_rotation_requests.splice(index, 1);
        } else {
            index = $scope.internship.forwarded_rotation_requests.indexOf(request);
            $scope.internship.forwarded_rotation_requests.splice(index, 1);
        }
        $scope.internship.closed_rotation_requests.push(request);
    };

    $scope.moveToForwardedRequests = function (request) {
        // Move request to *forwarded* requests
        var index = $scope.internship.unreviewed_rotation_requests.indexOf(request);  // WARNING: indexOf not supported in all browsers (IE7 & 8)
        $scope.internship.unreviewed_rotation_requests.splice(index, 1);

        $scope.internship.forwarded_rotation_requests.push(request);
    };

    $scope.getStatus = function (request) {
        if (!!request.response) {
            return request.response.is_approved ? "Approved" : "Declined";
        } else if (!!request.forward) {
            return "Forwarded";
        }
    };

    $scope.getClass = function (request) {
        var status = $scope.getStatus(request);
        if (status == "Approved") {
            return "success";
        } else {
            return "danger";
        }
    };

    $scope.getMomentFromMonthId = function (monthId) {
        var year = Math.floor(monthId/12);
        var month = monthId % 12;
        return moment({year: year, month: month, monthId: monthId});
    }
}])

.controller("PlansSummaryCtrl", ["$scope", "$q", "Batch", function ($scope, $q, Batch) {
    $scope.batches = Batch.query();

    $scope.batches.$promise.then(function (batches) {
        angular.forEach(batches, function (batch, index) {
            batch.search = function(query) {
                // Note that query can be undefined for two reasons:
                // 1. Because it is called as a getter and thus called with no arguments
                // 2. Because the property should actually be set to undefined. This happens e.g. if the
                //    input is invalid
                if (arguments.length) {
                    batch._query = query;
                    $scope.updatePage(batch, 1);
                } else {
                    return batch._query;
                }
            };
            $scope.updatePage(batch, 1);
        })
    });


    function shallowClearAndCopy(src, dst) {
        /* Create a shallow copy of an object and clear other fields from the destination */
        /* https://github.com/angular/angular.js/blob/master/src/ngResource/resource.js#L30 */
        dst = dst || {};
        angular.forEach(dst, function(value, key) {
            delete dst[key];
        });
        for (var key in src) {
            if (src.hasOwnProperty(key) && !(key.charAt(0) === '$' && key.charAt(1) === '$')) {
                dst[key] = src[key];
            }
        }
        return dst;
    }

    $scope.getPlansPage = function (batch, page, query) {
        var defer = $q.defer();
        var params = {id: batch.id, page: page};
        if (!!query) {params.query = query;}

        var value = Object.assign(
            batch.plans || {},
            {$promise: defer.promise}
        );

        Batch.plans(params, function (results, headers) {
            var promise = value.$promise;
            shallowClearAndCopy(results, value);
            value.$promise = promise;
            value.$resolved = true;
            value.$totalCount = headers('pagination-total');

            defer.resolve(results);
        });

        return value;
    };

    $scope.updatePage = function (batch, newPageNumber) {
        batch.plans = $scope.getPlansPage(batch, newPageNumber, batch._query);
    };

    $scope.offsetMonths = function (months, batchStartMonth, planStartMonth) {
        var diff = planStartMonth.diff(batchStartMonth, 'months');
        var offset = Array.apply(null, Array(diff)).map(function (value, index) {return index;}).concat(months);
        return offset;
    };

    $scope.requiresEllipsis = function (months, batchStartMonth, planStartMonth) {
        var offset = $scope.offsetMonths(months, batchStartMonth, planStartMonth);
        var sliced = offset.slice(12); // Get all months after the twelfth month
        var filtered = sliced.filter(function (month) {
            return month.disabled === false;
        });
        // A plan requires an ellipsis if there is at least one entry/month that is not `disabled`
        return filtered.length > 0;
    };
}]);
