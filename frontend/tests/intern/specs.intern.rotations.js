/**
 * Created by MSArabi on 12/10/16.
 */
describe('Rotation Request Page', function() {
    var serverUrl = "http://localhost:8081/";

    beforeAll(function() {
        browser.ignoreSynchronization = true;
        browser.get(serverUrl + "accounts/signin/");
        element(by.css("#id_identification")).sendKeys("testuser0");
        element(by.css("#id_password")).sendKeys("123");
        element(by.css("button[type=submit]")).click();
        browser.ignoreSynchronization = false;
    });

    it('should allow interns to submit rotations', function() {
        browser.get(serverUrl + "#/planner/24208/new/");

        element(by.model("rotationRequestData.department_specialty")).click();
        element(by.id("ui-select-choices-row-0-0")).click();
        element(by.model("rotationRequestData.department_hospital")).click();
        element(by.id("ui-select-choices-row-1-0")).click();
        element(by.buttonText("Submit")).click();

        expect(browser.getLocationAbsUrl()).toMatch(/planner\/$/g);

    });

    it('should allow interns to submit rotation requests to unlisted hospitals', function() {
        browser.get(serverUrl + "#/planner/24209/new/");

        element(by.model("rotationRequestData.department_specialty")).click();
        element(by.id("ui-select-choices-row-0-0")).click();
        element(by.model("rotationRequestData.department_hospital")).click();
        element(by.xpath('.//*[.="Other"]')).click();  // Select the element with the text "Other"

        element(by.id("id_new_hospital_name")).sendKeys("New Hospital Name");
        element(by.id("id_new_hospital_abbreviation")).sendKeys("NHN");
        element(by.id("id_new_hospital_contact_name")).sendKeys("New Hospital Contact Name");
        element(by.id("id_new_hospital_contact_position")).sendKeys("New Hospital Contact Position");
        element(by.id("id_new_hospital_email")).sendKeys("New Hospital Email");
        element(by.id("id_new_hospital_phone")).sendKeys("New Hospital Phone");
        element(by.id("id_new_hospital_extension")).sendKeys("New Hospital Extension");

        element(by.buttonText("Submit")).click();

        expect(browser.getLocationAbsUrl()).toMatch(/planner\/$/g);

    });

    it('should allow interns to partially submit new hospital data', function() {
        browser.get(serverUrl + "#/planner/24207/new/");

        element(by.model("rotationRequestData.department_specialty")).click();
        element(by.id("ui-select-choices-row-0-1")).click();
        element(by.model("rotationRequestData.department_hospital")).click();
        element(by.xpath('.//*[.="Other"]')).click();  // Select the element with the text "Other"

        element(by.id("id_new_hospital_name")).sendKeys("New Hospital Name");
        element(by.id("id_new_hospital_abbreviation")).sendKeys("NHN");

        element(by.buttonText("Submit")).click();

        browser.pause();

        expect(browser.getLocationAbsUrl()).toMatch(/planner\/$/g);
    });
});