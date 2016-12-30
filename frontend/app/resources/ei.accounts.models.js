/**
 * Created by MSArabi on 9/22/16.
 */
var accountsModule = angular.module('ei.accounts.models', ["ngResource"]);

accountsModule.factory("User", ["$resource", function ($resource) {
    return $resource('/api/users/:id', {id: '@id'});
}]);

accountsModule.factory("Profile", ["$resource", function($resource) {
    return $resource('/api/profiles/:id', {id: '@id'});
}]);

accountsModule.factory("Intern", ["$resource", function($resource) {
    return $resource('/api/interns/:id', {id: '@id'}, {
        as_table: {
            method: 'get',
            url: '/api/interns/as_table/',
            isArray: true
        }
    });
}]);
