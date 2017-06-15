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

.factory("LeaveRequest", ["$resource", function($resource) {
    return $resource('/api/leave_requests/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            transformResponse: [function (data, headersGetter) {
                var transformed = angular.fromJson(data);
                
                for (var i = 0; i < data.length; i++) {
                    // Convert month to moment
                    transformed[i].month = moment({
                        year: Math.floor(transformed[i].month / 12),
                        month: (transformed[i].month % 12)
                    });
                    
                    // Convert start and end dates into moment
                    transformed[i].start_date = moment(transformed[i].start_date);
                    transformed[i].end_date = moment(transformed[i].end_date);

                    // Convert submission datetime into moment
                    transformed[i].submission_datetime = moment(transformed[i].submission_datetime);
                }
                
                return transformed;
            }]
        },
        get: {
            method: 'get',
            transformResponse: [function (data, headersGetter) {
                var transformed = angular.fromJson(data);
                
                // Convert month to moment
                transformed.month = moment({
                    year: Math.floor(transformed.month / 12),
                    month: (transformed.month % 12)
                });
                
                // Convert start and end dates into moment
                transformed.start_date = moment(transformed.start_date);
                transformed.end_date = moment(transformed.end_date);

                // Convert submission datetime into moment
                transformed.submission_datetime = moment(transformed.submission_datetime);
                
                return transformed;
            }]
        },
        save: {
            method: 'post',
            transformRequest: [function (data, headersGetter) {
                data.month = data.month.year() * 12 + (data.month.month() - 1);

                data.start_date = data.start_date.toDate();
                data.end_date = data.end_date.toDate();

                return angular.toJson(data);
            }]
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