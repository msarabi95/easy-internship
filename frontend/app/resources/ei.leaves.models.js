/**
 * Created by MSArabi on 11/17/16.
 */
angular.module("ei.leaves.models", ["ngResource", "ei.interceptors"])

.factory("LeaveType", ["$resource", function($resource) {
    return $resource('/api/leave_types/:id', {id: '@id'});
}])

.factory("LeaveSetting", ["$resource", function($resource) {
    return $resource('/api/leave_settings/:id', {id: '@id'});
}])

.factory("LeaveRequest", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/leave_requests/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        }
    });
}])

.factory("LeaveRequestResponse", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/leave_request_responses/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        }
    });
}])

.factory("Leave", ["$resource", function($resource) {
    return $resource('/api/leaves/:id', {id: '@id'});
}])

.factory("LeaveCancelRequest", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/leave_cancel_requests/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        }
    });
}])

.factory("LeaveCancelRequestResponse", ["$resource", function($resource) {
    return $resource('/api/leave_cancel_request_responses/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["response_datetime"])
        }
    });
}]);