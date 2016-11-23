/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.rotations.models", ["ngResource"])

.factory("Rotation", ["$resource", function($resource) {
    return $resource('/api/rotations/:id', {id: '@id'});
}])

.factory("RequestedDepartment", ["$resource", function($resource) {
    return $resource('/api/requested_departments/:id', {id: '@id'});
}])

.factory("RotationRequest", ["$resource", function($resource) {
    return $resource('/api/rotation_requests/:id', {id: '@id'}, {
        query_by_department_and_month: {
            method: "get",
            url: '/api/rotation_requests/:department_id/:month_id',
            isArray: true
        },
        respond: {
            method: "post",
            url: '/api/rotation_requests/:id/respond/',
            params: {
                id: '@id'
            }
        },
        forward: {
            method: "post",
            url: '/api/rotation_requests/:id/forward/',
            params: {
                id: '@id'
            }
        }
    });
}])

.factory("RotationRequestResponse", ["$resource", function($resource) {
    return $resource('/api/rotation_request_responses/:id', {id: '@id'});
}])

.factory("RotationRequestForward", ["$resource", function($resource) {
    return $resource('/api/rotation_request_forwards/:key', {key: '@key'});
}])

.factory("RotationRequestForwardResponse", ["$resource", function($resource) {
    return $resource('/api/rotation_request_forward_responses/:id', {id: '@id'});
}]);