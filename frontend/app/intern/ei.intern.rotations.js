/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.rotations", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                              "ei.utils", "djng.forms", "ngResource", "ngRoute", "ngSanitize", "ngAnimate",
                              "ui.bootstrap", "ui.select", "ei.rotations.directives", "ngFileUpload"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/:month_id/history/", {
            templateUrl: "static/partials/intern/rotations/rotation-request-history.html?v=0006",
            controller: "RotationRequestHistoryCtrl"
        })
        .when("/planner/:month_id/request-rota/", {
            templateUrl: "static/partials/intern/rotations/request-rotation.html",
            controller: "RequestRotationCtrl"
        })
        .when("/planner/:month_id/cancel-rota/", {
            templateUrl: "static/partials/intern/rotations/request-rotation-cancel.html",
            controller: "RequestRotationCancelCtrl"
        })
        .when("/planner/:month_id/request-rota/delete/", {
            templateUrl: "static/partials/intern/rotations/delete-rotation-request.html?v=0001",
            controller: "DeleteRotationRequestCtrl"
        })
        .when("/planner/:month_id/cancel-rota/delete/", {
            templateUrl: "static/partials/intern/rotations/delete-rotation-cancel-request.html?v=0001",
            controller: "DeleteRotationCancelRequestCtrl"
        })

}])


.controller("RequestRotationCtrl", ["$scope", "$q", "$routeParams", "$location", "Upload", "Specialty", "Hospital", "Intern", "InternshipMonth", "RotationRequest",
    function ($scope, $q, $routeParams, $location, Upload, Specialty, Hospital, Intern, InternshipMonth, RotationRequest) {
        // Basic info about month and intern
        $scope.internshipMonth = InternshipMonth.get({month_id: $routeParams.month_id});
        Intern.query(function (interns) {
            $scope.intern = interns[0];
        });

        // Initialize request data to an empty object; load specialties
        $scope.rotation_request = {};
        $scope.specialties = Specialty.query();

        $scope.$watch('rotation_request.specialty', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== oldValue) {
                $scope.selected_hospital = undefined;
                $scope.rotation_request.hospital = undefined;
                $scope.rotation_request.department = undefined;
                $scope.hospitals = Hospital.query_with_acceptance_details({
                    month: $scope.internshipMonth.month,
                    specialty: newValue
                });

                if ($scope.intern.is_ksauhs_intern || $scope.intern.is_agu_intern) {
                    $scope.hospitals.$promise.then(function() {
                        $scope.hospitals.push({id: -1, name: "Other", abbreviation: "OTHER"});
                    })
                }
            }
        });

        $scope.$watch('rotation_request.hospital', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== oldValue) {
                // FIXME: dirty hack
                $scope.selected_hospital = $scope.hospitals.filter(function (hosp) {return hosp.id === newValue})[0];
            }
        });

        $scope.submit = function() {
            $scope.rotation_request.month = $scope.internshipMonth.month;
            $scope.rotation_request.internship = $scope.intern.internship;

            $scope.hospitalChosen = $q.defer();

            if ($scope.rotation_request.hospital === -1 && $scope.new_hospital_form.$valid) {
                var newHospital = new Hospital($scope.new_hospital);
                var resp = newHospital.$save();
                resp.then(function (response) {
                    $scope.hospitals = Hospital.query_with_acceptance_details({
                        month: $scope.internshipMonth.month,
                        specialty: $scope.rotation_request.specialty
                    });
                    if ($scope.intern.is_ksauhs_intern || $scope.intern.is_agu_intern) {
                        $scope.hospitals.$promise.then(function() {
                            $scope.hospitals.push({id: -1, name: "Other", abbreviation: "OTHER"});
                        })
                    }
                    $scope.hospitals.$promise.then(function () {
                        $scope.rotation_request.hospital = response.id;
                        $scope.new_hospital = {};
                        $scope.new_hospital_form.$setUntouched();
                        $scope.new_hospital_form.$setPristine();
                        // FIXME: dirty hack
                        $scope.selected_hospital = $scope.hospitals.filter(function (hosp) {return hosp.id === response.id})[0];
                        $scope.hospitalChosen.resolve();
                    });
                });
            } else {
                $scope.hospitalChosen.resolve();
            }

            $scope.hospitalChosen.promise.then(function() {
                // Set the department value if it hasn't been chosen through the department menu
                if ($scope.rotation_request_form.$valid && $scope.rotation_request.department === undefined) {
                    try {
                        $scope.rotation_request.department = $scope.selected_hospital.specialty_departments[0].id;
                    } catch (err) {
                        console.error(err);
                        toastr.warning(
                            "It seems we have a problem with getting your request information right. " +
                            "This shouldn't usually happen. " +
                            "Please contact us at support@easyinternship.net to fix it."
                        );
                        throw "Missing department info.";
                    }
                }

                // Submit
                $scope.upload = Upload.upload({
                    url: '/api/rotation_requests/',
                    data: $scope.rotation_request,
                    method: "POST"
                });
                $scope.upload.then(function (resp) {
                    $location.path('/planner');

                }, function (resp) {
                    if (resp.status !== 400) {
                        console.log(resp);
                        toastr.error(resp);
                    } else {
                        $scope.rotation_request_form.$message = resp.data.non_field_errors;
                        const fields = ['specialty', 'hospital', 'is_elective', 'request_memo', 'department'];
                        for (var i in fields) {
                            var item = fields[i];
                            if (!$scope.rotation_request_form[item]) {
                                continue;
                            }

                            $scope.rotation_request_form[item].$message = resp.data[item];
                            if (!!$scope.rotation_request_form[item].$message) {
                                $scope.rotation_request_form[item].$setPristine(true);
                            }
                        }
                    }
                });
            });
        };

        // This will be used in the template
        $scope.moment = moment;
}])

.controller("RotationRequestHistoryCtrl", ["$scope", "$routeParams", "Internship", function ($scope, $routeParams, Internship) {
    $scope.internship = Internship.query(function (internships) {
        $scope.internship = internships[0];
        $scope.month = $scope.internship.months.filter(function (month, index) {
            return month.month == $routeParams.month_id;
        })[0];

        $scope.request_history = [];
        $scope.request_history = $scope.request_history.concat($scope.month.rotation_request_history.map(function (request) {return Object.assign(request, {is_rotation_request: true});}));
        $scope.request_history = $scope.request_history.concat($scope.month.rotation_cancel_request_history.map(function (request) {return Object.assign(request, {is_rotation_cancel_request: true});}));
        $scope.request_history = $scope.request_history.concat($scope.month.freeze_request_history.map(function (request) {return Object.assign(request, {is_freeze_request: true});}));
        $scope.request_history = $scope.request_history.concat($scope.month.freeze_cancel_request_history.map(function (request) {return Object.assign(request, {is_freeze_cancel_request: true});}));

        angular.forEach($scope.request_history, function (request, index) {
            request.submission_datetime = moment(request.submission_datetime);
            request.response.response_datetime = moment(request.response.response_datetime);

            if (!!request.forward) {
                request.forward.forward_datetime = moment(request.forward.forward_datetime);
            }
        });
    });
}])

.controller("RequestRotationCancelCtrl", ["$scope", "$routeParams", "$location", "InternshipMonth",
    function ($scope, $routeParams, $location, InternshipMonth) {
    $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

    $scope.submit = function () {

        $scope.month.$cancel_rotation({}, function (data) {
            $location.path("/planner");
        }, function (error) {
            toastr.error(error.statusText);
        });

    };
}])

.controller("DeleteRotationRequestCtrl", ["$scope", "$routeParams", "$location", "Internship", "RotationRequest", function ($scope, $routeParams, $location, Internship, RotationRequest) {
    $scope.internship = Internship.query(function (internships) {
        $scope.internship = internships[0];
        $scope.month = $scope.internship.months.filter(function (month, index) {
            return month.month == $routeParams.month_id;
        })[0];

        $scope.request = $scope.month.current_rotation_request;
    });

    $scope.submit = function() {
        RotationRequest.delete({id: $scope.request.id}, function () {
            $location.path("/planner");
        }, function (error) {
            toastr.error(error.statusText);
        });
    };
}])

.controller("DeleteRotationCancelRequestCtrl", ["$scope", "$routeParams", "$location", "Internship", "RotationRequest", function ($scope, $routeParams, $location, Internship, RotationRequest) {
    $scope.internship = Internship.query(function (internships) {
        $scope.internship = internships[0];
        $scope.month = $scope.internship.months.filter(function (month, index) {
            return month.month == $routeParams.month_id;
        })[0];

        $scope.request = $scope.month.current_rotation_cancel_request;
    });

    $scope.submit = function() {
        RotationRequest.delete({id: $scope.request.id}, function () {
            $location.path("/planner");
        }, function (error) {
            toastr.error(error.statusText);
        });
    };
}]);