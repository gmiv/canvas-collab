/**
 * @file test_security.js
 * @description Security tests using OWASP ZAP API (requires OWASP ZAP to be running)
 */

// Ensure OWASP ZAP is running and the API is accessible
const ZapClient = require('zaproxy');
const { expect } = require('chai');

const zapOptions = {
  apiKey: '', // Set your OWASP ZAP API key if configured
  proxy: 'http://localhost:8080', // ZAP's default proxy
};

const zaproxy = new ZapClient(zapOptions);

describe('OWASP ZAP Security Tests', function () {
  this.timeout(600000); // Increase timeout due to scan duration
  const target = 'http://localhost:3000'; // Adjust as needed

  before((done) => {
    // Start OWASP ZAP or ensure it's running
    // Potentially start the application if not already running
    done();
  });

  it('should perform a passive scan and detect vulnerabilities', (done) => {
    // Start Spidering the target
    zaproxy.spider.scan(target, {}, (err, resp) => {
      if (err) return done(err);
      const scanId = resp.scan;
      const checkSpiderStatus = () => {
        zaproxy.spider.status(scanId, (err, statusResp) => {
          if (err) return done(err);
          const status = parseInt(statusResp.status);
          if (status < 100) {
            console.log(`Spider progress: ${status}%`);
            setTimeout(checkSpiderStatus, 5000);
          } else {
            console.log('Spider complete');
            // Start Active Scan
            zaproxy.ascan.scan(target, {}, (err, ascanResp) => {
              if (err) return done(err);
              const ascanId = ascanResp.scan;
              const checkActiveScanStatus = () => {
                zaproxy.ascan.status(ascanId, (err, aStatusResp) => {
                  if (err) return done(err);
                  const aStatus = parseInt(aStatusResp.status);
                  if (aStatus < 100) {
                    console.log(`Active Scan progress: ${aStatus}%`);
                    setTimeout(checkActiveScanStatus, 5000);
                  } else {
                    console.log('Active Scan complete');
                    // Get Alerts
                    zaproxy.core.alerts(
                      {
                        baseurl: target,
                        start: 0,
                        count: 9999,
                      },
                      (err, alertsResp) => {
                        if (err) return done(err);
                        const alerts = alertsResp.alerts;
                        // Analyze alerts
                        alerts.forEach((alert) => {
                          console.log(`Alert: ${alert.alert}`);
                          console.log(`Risk: ${alert.risk}`);
                          console.log(`Description: ${alert.description}`);
                        });
                        // Assert that high-risk vulnerabilities are not present
                        const highRiskAlerts = alerts.filter((alert) => alert.risk === 'High');
                        expect(highRiskAlerts.length).to.equal(0);
                        done();
                      }
                    );
                  }
                });
              };
              checkActiveScanStatus();
            });
          }
        });
      };
      checkSpiderStatus();
    });
  });
});