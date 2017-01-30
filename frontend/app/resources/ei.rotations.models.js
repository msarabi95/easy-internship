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
        query_by_department_and_month: {  // FIXME: Remove (no longer used)
            method: "get",
            url: '/api/rotation_requests/:department_id/:month_id',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        kamc_no_memo: {
            method: 'get',
            url: '/api/rotation_requests/kamc_no_memo/',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        kamc_memo: {
            method: 'get',
            url: '/api/rotation_requests/kamc_memo/',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        non_kamc: {
            method: 'get',
            url: '/api/rotation_requests/non_kamc/',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["submission_datetime"])
        },
        cancellation: {
            method: 'get',
            url: '/api/rotation_requests/cancellation/',
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
    return $resource('/api/rotation_request_forwards/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["forward_datetime", "last_updated"])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(["forward_datetime", "last_updated"])
        },
        intern_memos_as_table: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["forward_datetime"]),
            url: '/api/rotation_request_forwards/intern_memos_as_table/'
        },
        staff_memos_as_table: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["forward_datetime"]),
            url: '/api/rotation_request_forwards/staff_memos_as_table'
        },
        memos_archive_as_table: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(["forward_datetime"]),
            url: '/api/rotation_request_forwards/memos_archive_as_table'
        }
    });
}])

.factory("AcceptanceList", ["$resource", function ($resource) {
    return $resource('/api/acceptance_lists/:department_id/:month_id/', {
        department_id: '@department.id',
        month_id: '@month'
    }, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: {
                response: function (response) {
                    for (var x = 0; x < response.resource.length; x++) {
                        var list = response.resource[x];
                        var monthId = list.month;
                        response.resource[x].month = moment({year: Math.floor(monthId / 12), month: (monthId % 12), monthId: monthId});
                        for (var i = 0; i < list.auto_accepted.length; i++) {
                            response.resource[x].auto_accepted[i].submission_datetime = moment(response.resource[x].auto_accepted[i].submission_datetime);
                        }
                        for (var i = 0; i < list.auto_declined.length; i++) {
                            response.resource[x].auto_declined[i].submission_datetime = moment(response.resource[x].auto_declined[i].submission_datetime);
                        }
                    }
                    return response.resource;
                }
            }
        },
        respond: {
            method: 'post',
            url: '/api/acceptance_lists/:department_id/:month_id/respond/',
            params: {
                month_id: '@month._i.monthId'
            },
            transformRequest: function (data) {
                data.month = data.month._i.monthId;
                return angular.toJson(data);
            }
        }
    });
}]);