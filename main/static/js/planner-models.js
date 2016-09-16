/**
 * Created by MSArabi on 8/31/16.
 */
var plannerModule = angular.module("easy.planner", ["ngResource"]);

plannerModule.factory("Hospital", ["$resource", function($resource) {
    return $resource('/api/hospitals/:id', {id: '@id'});
}]);

plannerModule.factory("Specialty", ["$resource", function($resource) {
    return $resource('/api/specialties/:id', {id: '@id'});
}]);

plannerModule.factory("Department", ["$resource", function($resource) {
    return $resource('/api/departments/:id', {id: '@id'}, {
        get_by_specialty_and_hospital: {
            method: 'get',
            url: '/api/departments/:specialty/:hospital',
            params: {
                specialty: '@specialty',
                hospital: '@hospital'
            }
        }
    });
}]);

plannerModule.factory("SeatAvailability", ["$resource", function($resource) {
    return $resource('/api/seat_availabilities/:id', {id: '@id'});
}]);

plannerModule.factory("InternshipMonth", ["$resource", function($resource) {
    return $resource('/api/internship_months/:month_id', {month_id: '@month'}, {
        cancel_rotation: {
            method: 'post',
            url: '/api/internship_months/:month_id/cancel_rotation/',
            params: {
                month_id: '@month'
            }
        }
    });
}]);

plannerModule.factory("Internship", ["$resource", function($resource) {
    return $resource('/api/internships/:id', {id: '@id'});
}]);

plannerModule.factory("Rotation", ["$resource", function($resource) {
    return $resource('/api/rotations/:id', {id: '@id'});
}]);

plannerModule.factory("RequestedDepartment", ["$resource", function($resource) {
    return $resource('/api/requested_departments/:id', {id: '@id'});
}]);

plannerModule.factory("RotationRequest", ["$resource", function($resource) {
    return $resource('/api/rotation_requests/:id', {id: '@id'}, {
        submit: {
            method: "post",
            url: '/api/rotation_requests/submit/'
        }
    });
}]);

plannerModule.factory("RotationRequestResponse", ["$resource", function($resource) {
    return $resource('/api/rotation_request_responses/:id', {id: '@id'});
}]);

plannerModule.factory("RotationRequestForward", ["$resource", function($resource) {
    return $resource('/api/rotation_request_forwards/:key', {key: '@key'});
}]);

plannerModule.factory("RotationRequestForwardResponse", ["$resource", function($resource) {
    return $resource('/api/rotation_request_forward_responses/:id', {id: '@id'});
}]);
