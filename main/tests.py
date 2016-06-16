from django.test import TestCase


# TODO: Test redirect_to_index view, as well as bypassing it (e.g. admin/)
# Test 1: GET request to "" should work properly (code=200)
# Test 2: GET request to "hello/" should redirect to "/#/hello"
# Test 3: GET request to "admin/" should work properly (code=200)
# Test 4: AJAX GET request to "hello/" should work properly (code=200)
# Test 5: AJAX POST request to "hello/" should work properly (code=200)
# Note: AJAX URLs will normally be resolved before matching the `redirect_to_index` url,
#       but this still tests the integrity of the view itself
