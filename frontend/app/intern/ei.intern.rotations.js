/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.rotations", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                              "ei.utils", "djng.forms", "ngResource", "ngRoute", "ngSanitize", "ngAnimate",
                              "ui.bootstrap", "ui.select", "ei.rotations.directives", "ngFileUpload"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/:month_id/new/", {
            templateUrl: "static/partials/intern/rotations/rotation-request-create.html",
            controller: "RotationRequestCreateCtrl"
        })
        .when("/planner/:month_id/history/", {
            templateUrl: "static/partials/intern/rotations/rotation-request-history.html?v=0005",
            controller: "RotationRequestHistoryCtrl"
        })
        .when("/planner/:month_id/cancel/", {
            templateUrl: "static/partials/intern/rotations/rotation-cancel-request-create.html?v=0001",
            controller: "DeletionRequestCtrl"
        })

}])


.controller("RotationRequestCreateCtrl", ["$scope", "$routeParams", "$location", "Upload", "Specialty", "Hospital", "Intern", "InternshipMonth", "RotationRequest",
    function ($scope, $routeParams, $location, Upload, Specialty, Hospital, Intern, InternshipMonth, RotationRequest) {
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
                $scope.hospitals = Hospital.query_with_specialty_details({specialty: newValue});
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

            // Set the department value if it hasn't been chosen through the department menu
            if ($scope.rotation_request_form.$valid && $scope.rotation_request.department === undefined) {
                $scope.rotation_request.department = $scope.selected_hospital.specialty_departments[0].id;
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
                console.log(resp);
                toastr.error(resp);
            });
        };

        // This will be used in the template
        $scope.moment = moment;
}])

.controller("RotationRequestHistoryCtrl", ["$scope", "$routeParams", "loadWithRelated", "InternshipMonth", "RotationRequest", "RotationRequestResponse", "RotationRequestForward", "Specialty", "RequestedDepartment", "Department", "Hospital", "FreezeRequest", "FreezeRequestResponse", "FreezeCancelRequest", "FreezeCancelRequestResponse",
    function ($scope, $routeParams, loadWithRelated, InternshipMonth, RotationRequest, RotationRequestResponse, RotationRequestForward, Specialty, RequestedDepartment, Department, Hospital, FreezeRequest, FreezeRequestResponse, FreezeCancelRequest, FreezeCancelRequestResponse) {
        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.month.$promise.then(function (month) {

            console.log(month);


            $scope.month.rotation_request_history = loadWithRelated(month.rotation_request_history, RotationRequest, [
                {specialty: Specialty},
                {response: RotationRequestResponse},
                [{requested_department: RequestedDepartment}, [
                    [{department: Department}, [
                        {hospital: Hospital}
                    ]]
                ]]
            ]);

            $scope.month.rotation_request_history.$promise.then(function (requests) {
                angular.forEach(requests, function (request, index) {
                    request.is_rotation_request = true;
                    if (!!request.forward) {
                        request.forward = RotationRequestForward.get({id: request.forward});
                    }
                });
            });

            $scope.month.rotation_cancel_request_history = loadWithRelated(month.rotation_cancel_request_history, RotationRequest, [
                 {response: RotationRequestResponse}
            ]);
            $scope.month.rotation_cancel_request_history.$promise.then(function (requests) {
                angular.forEach(requests, function (request, index) {
                    request.is_rotation_cancel_request = true;
                });
            });

            $scope.month.freeze_request_history = loadWithRelated(month.freeze_request_history, FreezeRequest, [
                 {response: FreezeRequestResponse}
            ]);
            $scope.month.freeze_request_history.$promise.then(function (requests) {
                angular.forEach(requests, function (request, index) {
                    request.is_freeze_request = true;
                });
            });

            $scope.month.freeze_cancel_request_history = loadWithRelated(month.freeze_cancel_request_history, FreezeCancelRequest, [
                 {response: FreezeCancelRequestResponse}
            ]);
            $scope.month.freeze_cancel_request_history.$promise.then(function (requests) {
                angular.forEach(requests, function (request, index) {
                    request.is_freeze_cancel_request = true;
                });
            });

            $scope.request_history = [];
            $scope.request_history = $scope.request_history.concat($scope.month.rotation_request_history);
            $scope.request_history = $scope.request_history.concat($scope.month.rotation_cancel_request_history);
            $scope.request_history = $scope.request_history.concat($scope.month.freeze_request_history);
            $scope.request_history = $scope.request_history.concat($scope.month.freeze_cancel_request_history);

        });
}])

.controller("DeletionRequestCtrl", ["$scope", "$routeParams", "$location", "InternshipMonth",
    function ($scope, $routeParams, $location, InternshipMonth) {
    $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

    $scope.submit = function () {

        $scope.month.$cancel_rotation({}, function (data) {
            $location.path("/planner");
        }, function (error) {
            toastr.error(error.statusText);
        });

    };
}]);