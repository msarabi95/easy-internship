/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.rotations", ["ei.hospitals.models", "ei.months.models", "ei.rotations.models", "ei.leaves.models",
                              "ei.utils", "djng.forms", "ngResource", "ngRoute", "ngSanitize", "ngAnimate",
                              "ui.bootstrap", "ui.select"])

.config(["$routeProvider", function ($routeProvider) {

    $routeProvider
        .when("/planner/:month_id/new/", {
            templateUrl: "planner/rotation-request-form/",
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


.controller("RotationRequestCreateCtrl", ["$scope", "$routeParams", "$location", "Specialty", "Hospital", "Department",
    "RequestedDepartment", "RotationRequest", "InternshipMonth", "djangoForm", "$http", "$compile", "AcceptanceSettings",
    function ($scope, $routeParams, $location, Specialty, Hospital, Department, RequestedDepartment, RotationRequest, InternshipMonth, djangoForm, $http, $compile, AcceptanceSettings) {
        $scope.internshipMonth = InternshipMonth.get({month_id: $routeParams.month_id});

        $scope.showHospitalFields = false;
        $scope.disableHospitalMenu = true;
        $scope.rotationRequestData = {};
        $scope.specialties = Specialty.query();

        $scope.$watch('rotationRequestData.department_specialty', function (newValue, oldValue) {
            if (newValue !== oldValue) {
                $scope.disableHospitalMenu = true;
                $scope.showDepartmentMenu = false;
                if (newValue !== undefined && newValue !== "") {
                    $scope.getDepartments();
                } else {
                    $scope.rotationRequestData = {};  // reset form when specialty selection is changed
                }
            }
        });

        $scope.getDepartments = function () {
            // Load hospital data, each with the department corresponding to the selected specialty

            $scope.hospitals = Hospital.query(function (hospitals) {
                angular.forEach(hospitals, function (hospital, index) {
                    $scope.hospitals[index].specialty_departments = Department.get_by_specialty_and_hospital({
                        specialty: $scope.rotationRequestData.department_specialty,
                        hospital: $scope.hospitals[index].id
                    });

                    $scope.hospitals[index].specialty_departments.$promise.then(function (departments) {
                        angular.forEach(departments, function (department, dIndex) {
                            // Get acceptance settings
                            $scope.hospitals[index].specialty_departments[dIndex].acceptance_settings = AcceptanceSettings.get({}, {
                                department: department.id,
                                month: $scope.internshipMonth.month
                            });
                            $scope.hospitals[index].specialty_departments[dIndex].acceptance_settings.$promise.then(
                                function (settings) {
                                    /*console.log(settings);*/
                                },
                                function (error) {
                                    if (error.status !== 404) {
                                        toastr.error(error.statusText);
                                        console.error(error.statusText);
                                    }
                                });
                        });

                    }, function (error) {
                        if (error.status !== 404) {
                            toastr.error(error.statusText);
                            console.error(error.statusText);
                        }
                    });

                });

                $scope.hospitals.push({id: -1, name: "Other", abbreviation: "OTHER"});

                $scope.disableHospitalMenu = false;
            });
        };

        $scope.$watch('rotationRequestData.department_hospital', function (newValue, oldValue) {
            // Show or hide department detail fields based on whether department info is present in db or not
            if (newValue !== undefined && newValue !== oldValue) {
                if (newValue !== -1) {
                    $scope.showHospitalFields = false;

                    var hospital = $scope.hospitals.find(function (obj, index) {
                        return obj.id == newValue;
                    });

                    if (hospital.specialty_departments.length == 1) {
                        $scope.showDepartmentMenu = false;
                        var department = hospital.specialty_departments[0];
                        $scope.rotationRequestData.department = department.id;
                        $scope.rotationRequestData.is_in_database = true;
                    } else if (hospital.specialty_departments.length > 1) {
                        $scope.showDepartmentMenu = true;
                        $scope.rotationRequestData.is_in_database = true;
                        $scope.departmentMenuHospital = hospital;
                    } else {
                        $scope.showDepartmentMenu = false;
                        $scope.rotationRequestData.is_in_database = false;
                    }
                } else {
                    $scope.rotationRequestData.is_in_database = true;
                    $scope.showHospitalFields = true;
                }

            }
        });

        $scope.$watch('rotationRequestForm.$message', function (newValue, oldValue) {
            if (newValue !== undefined && newValue !== "") {
                toastr.warning(newValue);
                $scope.rotationRequestForm.$message = undefined;
            }
        });

        $scope.submit = function () {
            if ($scope.rotationRequestData) {

                $scope.rotationRequestData.month = $routeParams.month_id;

                $http.post(
                    "/planner/rotation-request-form/",
                    $scope.rotationRequestData
                ).success(function (out_data) {
                    if (!djangoForm.setErrors($scope.rotationRequestForm, out_data.errors)) {
                        $location.path("/planner");
                    }
                }).error(function (error) {
                    console.log(error);
                    toastr.error(error);
                })
            }

            return false;
        };

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