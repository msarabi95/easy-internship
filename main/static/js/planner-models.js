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
    return $resource('/api/departments/:id', {id: '@id'});
}]);

plannerModule.factory("SeatAvailability", ["$resource", function($resource) {
    return $resource('/api/seat_availabilities/:id', {id: '@id'});
}]);

plannerModule.factory("InternshipMonth", ["$resource", function($resource) {
    return $resource('/api/internship_months/:month', {month: '@month'});
}]);

plannerModule.factory("Internship", ["$resource", function($resource) {
    return $resource('/api/internships/:id', {id: '@id'});
}]);

plannerModule.factory("Rotation", ["$resource", function($resource) {
    return $resource('/api/rotations/:id', {id: '@id'});
}]);

plannerModule.factory("PlanRequest", ["$resource", function($resource) {
    return $resource('/api/plan_requests/:id', {id: '@id'});
}]);

plannerModule.factory("RequestedDepartment", ["$resource", function($resource) {
    return $resource('/api/requested_departments/:id', {id: '@id'});
}]);

plannerModule.factory("RotationRequest", ["$resource", function($resource) {
    return $resource('/api/rotation_requests/:id', {id: '@id'});
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
