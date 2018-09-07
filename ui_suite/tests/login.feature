Feature: login
    Login feature of appliance would be tested here

Scenario: Login with valid credentials
    Given Navigate to appliance
    And Enter valid password 
    And Click on login button
    Then Login successful and home page is displayed


Scenario: Login with invalid credentials
    Given Navigate to appliance
    And Enter invalid password
    And Click on login button
    Then Login should be unsuccessful and home page is displayed

