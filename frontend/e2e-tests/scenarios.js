'use strict';

/* https://github.com/angular/protractor/blob/master/docs/toc.md */

describe('my app', function() {

  browser.get('index.html');

  it('should automatically redirect to /LoginView when location hash/fragment is empty', function() {
    expect(browser.getLocationAbsUrl()).toMatch("/LoginView");
  });


  describe('LoginView', function() {

    beforeEach(function() {
      browser.get('index.html#/LoginView');
    });


    it('should render LoginView when user navigates to /LoginView', function() {
      expect(element.all(by.css('[ng-view] p')).first().getText()).
        toMatch(/partial for view 1/);
    });

  });


  describe('home', function() {

    beforeEach(function() {
      browser.get('index.html#/home');
    });


    it('should render home when user navigates to /home', function() {
      expect(element.all(by.css('[ng-view] p')).first().getText()).
        toMatch(/partial for view 2/);
    });

  });
});
