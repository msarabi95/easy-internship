/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.rotations", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                              "ei.utils", "djng.forms", "ngResource", "ngRoute", "ngSanitize", "ngAnimate",
                              "ui.bootstrap", "ui.select"])

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
            controller: "RotationCancelRequestCreateCtrl"
        })

}])


.controller("RotationRequestCreateCtrl", ["$scope", "$routeParams", "$location", "Specialty", "Hospital", "Location",
    "RotationRequest", "InternshipMonth", "AcceptanceSettings", "SeatSettings",
    function ($scope, $routeParams, $location, Specialty, Hospital, Location, RotationRequest, InternshipMonth, AcceptanceSettings, SeatSettings) {
        $scope.internshipMonth = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.rotation_request = {};

        $scope.specialties = Specialty.query();
        $scope.hospitals = Hospital.query();

        $scope.$watchGroup(['rotation_request.specialty', 'rotation_request.hospital'], function (newValues, oldValues, scope) {
            var specialty = newValues[0], oldSpecialty = oldValues[0];
            var hospital = newValues[1], oldHospital = oldValues[1];

            if (specialty !== undefined && hospital !== undefined) {
                if (specialty !== oldSpecialty || hospital !== oldHospital) {

                    // Clear old info
                    $scope.rotation_request.location = undefined;
                    clearSettings();

                    $scope.locations = Location.query({hospital: hospital, specialty: specialty});
                    $scope.locations.$promise.then(function (locations) {

                        if (locations.length == 0) {

                            retrieveSettings(
                                $scope.internshipMonth.month,
                                specialty,
                                hospital
                            )

                        }
                    })
                }
            }
        });

        $scope.$watch('rotation_request.location', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== oldValue) {
                retrieveSettings(
                    $scope.internshipMonth.month,
                    $scope.rotation_request.specialty,
                    $scope.rotation_request.hospital,
                    newValue
                );
            }
        });

        function retrieveSettings(month, specialty, hospital, location) {
            $scope.acceptance_setting = AcceptanceSettings.get({
                month_id: month,
                specialty: specialty,
                hospital: hospital,
                location: location == undefined ? null : location
            });

            $scope.seat_setting = SeatSettings.get({
                month_id: month,
                specialty: specialty,
                hospital: hospital,
                location: location == undefined ? null : location
            });
        }

        function clearSettings() {
            $scope.acceptance_setting = undefined;
            $scope.seat_setting = undefined;
        }

}])

.controller("RotationRequestHistoryCtrl", ["$scope", "$filter", "$routeParams", "loadWithRelated", "InternshipMonth", "RotationRequest", "RotationRequestForward", "RotationRequestResponse", "RotationCancelRequest", "RotationCancelRequestResponse", "Specialty", "Hospital", "Location",
    function ($scope, $filter, $routeParams, loadWithRelated, InternshipMonth, RotationRequest, RotationRequestForward, RotationRequestResponse, RotationCancelRequest, RotationCancelRequestResponse, Specialty, Hospital, Location) {
        $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.month.$promise.then(function (month) {

            $scope.month.rotation_request_history = loadWithRelated(month.rotation_request_history, RotationRequest, [
                {specialty: Specialty},
                {hospital: Hospital},
                {location: Location},
                {forward: RotationRequestForward},
                {response: RotationRequestResponse}
            ]);

            $scope.month.rotation_cancel_request_history = loadWithRelated(month.rotation_cancel_request_history, RotationCancelRequest, [
                {response: RotationCancelRequestResponse}
            ]);

            $scope.month.request_history = $scope.month.rotation_request_history.concat($scope.month.rotation_cancel_request_history);

        });
}])

.controller("RotationCancelRequestCreateCtrl", ["$scope", "$routeParams", "$location", "InternshipMonth", "Rotation", "RotationCancelRequest",
    function ($scope, $routeParams, $location, InternshipMonth, Rotation, RotationCancelRequest) {
    $scope.month = InternshipMonth.get({month_id: $routeParams.month_id});

    $scope.month.$promise.then(function (month) {
        $scope.month.current_rotation = Rotation.get({id: $scope.month.current_rotation});
    });

    $scope.submit = function () {

        var cancel_request = new RotationCancelRequest({
            internship: $scope.month.internship,
            month: $scope.month.month,
            specialty: $scope.month.current_rotation.specialty ,
            hospital: $scope.month.current_rotation.hospital,
            location: $scope.month.current_rotation.location,
            is_delete: true
        });

        cancel_request.$save({}, function (data) {
            $location.path("/planner");
        }, function (error) {
            toastr.error(error.statusText);
        });

    };
}]);