/**
 * Created by MSArabi on 9/22/16.
 */
angular.module('ei.accounts.models', ["ngResource", "ei.interceptors"])

.factory("User", ["$resource", function ($resource) {
    return $resource('/api/users/:id', {id: '@id'});
}])

.factory("Profile", ["$resource", function($resource) {
    return $resource('/api/profiles/:id', {id: '@id'});
}])

.factory("Intern", ["$resource", "DateTimeFieldToMomentInterceptor", function($resource, DateTimeFieldToMomentInterceptor) {
    return $resource('/api/interns/:id', {id: '@id'}, {
        query: {
            method: 'get',
            isArray: true,
            interceptor: DateTimeFieldToMomentInterceptor(['graduation_date'])
        },
        get: {
            method: 'get',
            interceptor: DateTimeFieldToMomentInterceptor(['graduation_date'])
        },
        as_table: {
            method: 'get',
            url: '/api/interns/as_table/',
            isArray: true
        }
    });
}])

.factory("Batch", ["$resource", function($resource) {
    return $resource('/api/batches/:id', {id: '@id'}, {
        interns: {
            method: 'get',
            url: '/api/batches/:id/interns',
            isArray: true
        }
    })
}]);
