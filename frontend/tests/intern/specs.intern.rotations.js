/**
 * Created by MSArabi on 12/10/16.
 */
describe('Rotation Request Page', function() {
    var serverUrl = "http://localhost:8081/";

    // FIXME: Not working

    beforeEach(function() {
        browser.get(serverUrl + "accounts/signin/");
        element(by.css("#id_identification]")).sendKeys("testuser0");
        element(by.css("#id_password")).sendKeys("123");
        element(by.css("button[type=submit]")).click();
    });

    it('should allow interns to submit rotations', function() {
        browser.get(serverUrl + "#/planner/24210/");

        element(by.model("rotationRequestData.department_specialty")).sendKeys("Internal Medicine");
        element(by.model("rotationRequestData.department_hospital")).sendKeys("King Abdulaziz Medical City");


    })
});