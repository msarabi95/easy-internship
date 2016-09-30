/**
 * Created by MSArabi on 7/14/16.
 */
var app = angular.module("easyInternship", ["ngRoute", "ngResource", "easy.planner", "easy.accounts", "ui.bootstrap"]);

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

app.controller("InternListCtrl", ["$scope", "Internship", "Intern", "Profile", function ($scope, Internship, Intern, Profile) {
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
}]);

app.controller("InternDetailCtrl", ["$scope", "$routeParams", "$timeout", "Internship", "Intern", "Profile", "User", "InternshipMonth", "RotationRequest", "RequestedDepartment", "Specialty", "Department", "Hospital", "RotationRequestResponse", "RotationRequestForward", "RotationRequestForwardResponse",
    function ($scope, $routeParams, $timeout, Internship, Intern, Profile, User, InternshipMonth, RotationRequest, RequestedDepartment, Specialty, Department, Hospital, RotationRequestResponse, RotationRequestForward, RotationRequestForwardResponse) {
        $scope.internship = Internship.get({id: $routeParams.id});

        $scope.internship.$promise.then(function (internship) {

            $scope.internship.intern = Intern.get({id: internship.intern});
            $scope.internship.intern.$promise.then(function (intern) {
                $scope.internship.intern.profile = Profile.get({id: intern.profile});
                $scope.internship.intern.profile.$promise.then(function (profile) {
                    $scope.internship.intern.profile.user = User.get({id: profile.user});
                })
            });

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
                    //$scope.internship[type + "_rotation_requests"][index].month =
                    //    InternshipMonth.get({month_id: request.month});

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
