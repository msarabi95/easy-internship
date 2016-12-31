/**
 * Created by MSArabi on 12/4/16.
 */
angular.module("ei.staff.accounts", ["ei.months.models", "ei.accounts.models",
                                     "ei.utils", "ei.rotations.directives", "ngRoute",
                                     "datatables", "datatables.bootstrap",
                                     "ui.bootstrap", "ui.select"])

.config(["$routeProvider", function ($routeProvider) {
    $routeProvider
        .when("/interns/", {
            templateUrl: "static/partials/staff/interns/intern-list.html?v=0001",
            controller: "InternListCtrl"
        })
        .when("/interns/:id/", {
            templateUrl: "static/partials/staff/interns/intern-detail.html?v=0004",
            controller: "InternDetailCtrl"
        });
}])

.controller("InternListCtrl", ["$scope", "DTOptionsBuilder", "DTColumnBuilder", "DTColumnDefBuilder", "Intern", "Profile",
    function ($scope, DTOptionsBuilder, DTColumnBuilder, DTColumnDefBuilder, Intern, Profile) {
        //$scope.internships = Internship.query();
        //
        //$scope.internships.$promise.then(function (internships) {
        //    angular.forEach(internships, function (internship, index) {
        //        // Load the intern profile and standard profile
        //        $scope.internships[index].intern = Intern.get({id: internship.intern});
        //        $scope.internships[index].intern.$promise.then(function (intern) {
        //            $scope.internships[index].intern.profile = Profile.get({id: intern.profile});
        //        });
        //    });
        //});

        /* FIXME:
        * - Load datatable data from a dedicated endpoint.
        * - Display more info.
        * - Fix search and sorting issues.
        * */
        $scope.dtOptions = DTOptionsBuilder
            .fromFnPromise(function() {
                return Intern.as_table().$promise;
            })
            .withOption("order", [[ 1, "asc" ]])
            .withOption("responsive", true)
            .withBootstrap();

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

        //$scope.dtColumns = [
        //    DTColumnDefBuilder.newColumnDef(0).notSortable(),
        //    DTColumnDefBuilder.newColumnDef([1, 2]).withOption("width", "20%"),
        //    DTColumnDefBuilder.newColumnDef(5).notSortable()
        //];
}])

.controller("InternDetailCtrl", ["$scope", "$routeParams", "$timeout", "$q", "loadWithRelated", "Internship", "Intern", "Profile", "User", "InternshipMonth",
    "RotationRequest", "RequestedDepartment", "Specialty", "Department", "Hospital", "RotationRequestResponse", "RotationRequestForward",
    "Rotation",
    function ($scope, $routeParams, $timeout, $q, loadWithRelated, Internship, Intern, Profile, User, InternshipMonth, RotationRequest, RequestedDepartment,
              Specialty, Department, Hospital, RotationRequestResponse, RotationRequestForward, Rotation) {
        $scope.internship = loadWithRelated($routeParams.id, Internship, [
            [{intern: Intern}, [
                [{profile: Profile}, [
                    {user: User}
                ]]
            ]]
        ], true);

        $scope.internship.$promise.then(function () {

            var startMonth = $scope.internship.start_month.split("-");

            startMonth = parseInt(startMonth[0]) * 12 + parseInt(startMonth[1]) - 1;

            $scope.internship.months = Array.apply(null, Array(15)).map(function (_, i) {return startMonth + i;});

            var promises = [];

            angular.forEach($scope.internship.months, function (month_id, index) {
                $scope.internship.months[index] = InternshipMonth.get_by_internship_and_id({internship_id: $scope.internship.id, month_id: month_id});

                promises.push($scope.internship.months[index].$promise);

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

            $scope.internship.months.$promise = $q.all(promises);

            $scope.months = $scope.internship.months; // a handy shortcut

            console.log($scope.internship);

            $scope.internship.rotation_requests = loadWithRelated($scope.internship.rotation_requests, RotationRequest);

            $scope.internship.rotation_requests.$promise.then(function (rotation_requests) {

                $scope.internship.unreviewed_rotation_requests = [];
                $scope.internship.forwarded_rotation_requests = [];
                $scope.internship.closed_rotation_requests = [];

                angular.forEach(rotation_requests, function (rotation_request, index) {

                    rotation_request.month = InternshipMonth.get_by_internship_and_id({month_id: rotation_request.month, internship_id: $scope.internship.id});
                    var promises = [rotation_request.month.$promise];

                    if (!!rotation_request.response) {
                        rotation_request.response = RotationRequestResponse.get({id: rotation_request.response});
                        rotation_request.specialty = Specialty.get({id: rotation_request.specialty});
                        rotation_request.requested_department = loadWithRelated(rotation_request.requested_department, RequestedDepartment, [
                            [{department: Department}, [
                                {hospital: Hospital}
                            ]]
                        ], true);
                        if (!!rotation_request.forward) {
                            rotation_request.forward = RotationRequestForward.get({id: rotation_request.forward});
                            promises.push(rotation_request.forward.$promise);
                        }

                        promises.push(rotation_request.response.$promise);
                        promises.push(rotation_request.specialty.$promise);
                        promises.push(rotation_request.requested_department.$promise);

                        rotation_request.$promise = rotation_request.$promise.then(function () {
                            return $q.all(promises);
                        });

                        $scope.internship.closed_rotation_requests.push(rotation_request);

                    } else if (!!rotation_request.forward) {
                        rotation_request.forward = RotationRequestForward.get({id: rotation_request.forward});
                        rotation_request.specialty = Specialty.get({id: rotation_request.specialty});
                        rotation_request.requested_department = loadWithRelated(rotation_request.requested_department, RequestedDepartment, [
                            [{department: Department}, [
                                {hospital: Hospital}
                            ]]
                        ], true);

                        promises.push(rotation_request.forward.$promise);
                        promises.push(rotation_request.specialty.$promise);
                        promises.push(rotation_request.requested_department.$promise);

                        rotation_request.$promise = rotation_request.$promise.then(function () {
                            return $q.all(promises);
                        });

                        $scope.internship.forwarded_rotation_requests.push(rotation_request);
                    } else {
                        rotation_request.specialty = Specialty.get({id: rotation_request.specialty});
                        rotation_request.requested_department = loadWithRelated(rotation_request.requested_department, RequestedDepartment, [
                            [{department: Department}, [
                                {hospital: Hospital}
                            ]]
                        ]);

                        promises.push(rotation_request.specialty.$promise);
                        promises.push(rotation_request.requested_department.$promise);

                        rotation_request.$promise = rotation_request.$promise.then(function () {
                            return $q.all(promises);
                        });

                        $scope.internship.unreviewed_rotation_requests.push(rotation_request);
                    }
                });
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
        }
}]);
