/**
 * Created by MSArabi on 11/23/16.
 */
angular.module("ei.rotations.models", ["ngResource", "ei.interceptors"])

.factory("Rotation", ["$resource", function($resource) {
    return $resource('/api/rotations/:id', {id: '@id'});
}])

.factory("RequestedDepartment", ["$resource", function($resource) {
    return $resource('/api/requested_departments/:id', {id: '@id'});
}])

.factory("RotationRequest", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/rotation_requests/:id', {id: '@id'}, {
        query: {
            method: "get",
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        get: {
            method: "get",
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        query_by_department_and_month: {
            method: "get",
            url: '/api/rotation_requests/:department_id/:month_id',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
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

.factory("RotationRequestResponse", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/rotation_request_responses/:id', {id: '@id'},{
        query: {
            method: "get",
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        get: {
            method: "get",
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        }
    });
}])

.factory("RotationRequestForward", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/rotation_request_forwards/:key', {key: '@key'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["forward_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["forward_datetime"])
        }
    });
}]);