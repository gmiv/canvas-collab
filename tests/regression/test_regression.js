/**
 * @file test_regression.js
 * @description Regression test suite
 */

const { exec } = require('child_process');

describe('Regression Test Suite', () => {
  it('runs all unit tests', (done) => {
    exec('npm run test:unit', (error, stdout, stderr) => {
      if (error) {
        console.error(`Unit tests failed: ${stderr}`);
        done(error);
      } else {
        console.log(stdout);
        done();
      }
    });
  });

  it('runs all integration tests', (done) => {
    exec('npm run test:integration', (error, stdout, stderr) => {
      if (error) {
        console.error(`Integration tests failed: ${stderr}`);
        done(error);
      } else {
        console.log(stdout);
        done();
      }
    });
  });

  it('runs all system tests', (done) => {
    exec('npm run test:system', (error, stdout, stderr) => {
      if (error) {
        console.error(`System tests failed: ${stderr}`);
        done(error);
      } else {
        console.log(stdout);
        done();
      }
    });
  });
});