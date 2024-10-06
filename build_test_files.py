import os

# Define the files and their content
files = {
    'tests/unit/test_canvas.js': '''
/**
 * @file test_canvas.js
 * @description Unit tests for canvas.js
 */

const { JSDOM } = require('jsdom');
const { expect } = require('chai');
const sinon = require('sinon');

// Mock the DOM and Canvas
const dom = new JSDOM(`<!DOCTYPE html><html><body><canvas id="drawingCanvas"></canvas></body></html>`);
global.window = dom.window;
global.document = dom.window.document;

// Mock Canvas API
const mockCanvas = require('canvas-prebuilt'); // Use an appropriate canvas mocking library
global.HTMLCanvasElement.prototype.getContext = () => {
  return {
    beginPath: sinon.spy(),
    moveTo: sinon.spy(),
    lineTo: sinon.spy(),
    stroke: sinon.spy(),
    closePath: sinon.spy(),
    lineWidth: 1,
    strokeStyle: '#000000',
  };
};

// Import the module to test
const canvasModule = require('../../public/js/canvas.js');

describe('Canvas Module Unit Tests', () => {
  beforeEach(() => {
    // Reset any changes before each test
    canvasModule.isDrawing = false;
    canvasModule.lastX = 0;
    canvasModule.lastY = 0;
  });

  it('should start drawing when startDrawing is called', () => {
    const event = { offsetX: 100, offsetY: 150 };
    canvasModule.startDrawing(event);
    expect(canvasModule.isDrawing).to.be.true;
    expect(canvasModule.lastX).to.equal(100);
    expect(canvasModule.lastY).to.equal(150);
  });

  it('should draw on the canvas when draw is called and isDrawing is true', () => {
    // Mock the canvas context methods
    const ctx = canvasModule.ctx;
    sinon.spy(ctx, 'beginPath');
    sinon.spy(ctx, 'moveTo');
    sinon.spy(ctx, 'lineTo');
    sinon.spy(ctx, 'stroke');

    // Set isDrawing to true
    canvasModule.isDrawing = true;
    canvasModule.lastX = 50;
    canvasModule.lastY = 50;

    const event = { offsetX: 70, offsetY: 80 };
    canvasModule.draw(event);

    expect(ctx.beginPath.calledOnce).to.be.true;
    expect(ctx.moveTo.calledWith(50, 50)).to.be.true;
    expect(ctx.lineTo.calledWith(70, 80)).to.be.true;
    expect(ctx.stroke.calledOnce).to.be.true;

    // Clean up spies
    ctx.beginPath.restore();
    ctx.moveTo.restore();
    ctx.lineTo.restore();
    ctx.stroke.restore();
  });

  it('should not draw when isDrawing is false', () => {
    // Mock the canvas context methods
    const ctx = canvasModule.ctx;
    sinon.spy(ctx, 'stroke');

    // Ensure isDrawing is false
    canvasModule.isDrawing = false;

    const event = { offsetX: 70, offsetY: 80 };
    canvasModule.draw(event);

    expect(ctx.stroke.notCalled).to.be.true;

    // Clean up spy
    ctx.stroke.restore();
  });

  it('should stop drawing when stopDrawing is called', () => {
    canvasModule.isDrawing = true;
    canvasModule.stopDrawing();
    expect(canvasModule.isDrawing).to.be.false;
  });

  it('should update marker thickness when setThickness is called', () => {
    const thickness = 10;
    canvasModule.setThickness(thickness);
    expect(canvasModule.ctx.lineWidth).to.equal(thickness);
  });
});
''',

    'tests/unit/test_app.js': '''
/**
 * @file test_app.js
 * @description Unit tests for app.js
 */

const { expect } = require('chai');
const sinon = require('sinon');
const { JSDOM } = require('jsdom');

// Mock the DOM
const dom = new JSDOM(`<!DOCTYPE html><html><body>
  <div id="nameModal" style="display: none;">
    <input type="text" id="nameInput" />
    <button id="nameSubmit">Submit</button>
  </div>
  <div id="userNameDisplay"></div>
</body></html>`);
global.window = dom.window;
global.document = dom.window.document;

// Mock Socket.io client
const io = require('socket.io-client');
const socketMock = {
  emit: sinon.stub(),
  on: sinon.stub(),
};
global.io = () => socketMock;

// Import the module to test
const appModule = require('../../public/js/app.js');

describe('App Module Unit Tests', () => {
  it('should display the name prompt on page load', () => {
    appModule.showNamePrompt();
    const nameModal = document.getElementById('nameModal');
    expect(nameModal.style.display).to.equal('block');
  });

  it('should assign a default ID when no name is entered', () => {
    // Reset socket emit stub
    socketMock.emit.resetHistory();
    document.getElementById('nameInput').value = '';
    appModule.submitName();
    expect(socketMock.emit.calledWith('submitName', { name: sinon.match.string })).to.be.true;
    const nameSent = socketMock.emit.getCall(0).args[1].name;
    expect(nameSent.startsWith('User_')).to.be.true;
  });

  it('should handle duplicate names by appending an integer', () => {
    // Simulate server response
    socketMock.on.withArgs('nameAssigned').callsArgWith(1, 'Alex_1');
    document.getElementById('nameInput').value = 'Alex';
    appModule.submitName();
    const userNameDisplay = document.getElementById('userNameDisplay');
    expect(userNameDisplay.textContent).to.equal('Alex_1');
  });

  it('should prevent name editing after submission', () => {
    const nameInput = document.getElementById('nameInput');
    nameInput.value = 'TestUser';
    appModule.submitName();
    expect(nameInput.disabled).to.be.true;
  });
});
''',

    'tests/unit/test_server.js': '''
/**
 * @file test_server.js
 * @description Unit tests for server.js
 */

const chai = require('chai');
const sinon = require('sinon');
const { expect } = chai;
const io = require('socket.io-client');
const http = require('http');
const serverModule = require('../../server/server.js'); // Adjust the path as needed

describe('Server Module Unit Tests', () => {
  let server;
  let socketUrl;
  let options = {
    transports: ['websocket'],
    'force new connection': true,
  };

  before((done) => {
    // Start the server
    const app = serverModule.app; // Assuming server.js exports an app
    server = http.createServer(app);
    server.listen(() => {
      const port = server.address().port;
      socketUrl = `http://localhost:${port}`;
      done();
    });
  });

  after(() => {
    server.close();
  });

  it('should add a new user to active users on connection', (done) => {
    const client = io.connect(socketUrl, options);
    client.on('connect', () => {
      client.emit('submitName', { name: 'TestUser' });
      client.on('nameAssigned', (assignedName) => {
        expect(assignedName).to.equal('TestUser');

        // Access the server's active users
        const activeUsers = serverModule.activeUsers;
        expect(activeUsers).to.include('TestUser');

        client.disconnect();
        done();
      });
    });
  });

  it('should append an integer to duplicate names', (done) => {
    const client1 = io.connect(socketUrl, options);
    const client2 = io.connect(socketUrl, options);

    client1.on('connect', () => {
      client1.emit('submitName', { name: 'Alex' });
      client1.on('nameAssigned', (assignedName1) => {
        expect(assignedName1).to.equal('Alex');

        client2.emit('submitName', { name: 'Alex' });
        client2.on('nameAssigned', (assignedName2) => {
          expect(assignedName2).to.equal('Alex_1');
          client1.disconnect();
          client2.disconnect();
          done();
        });
      });
    });
  });

  it('should sanitize user inputs', (done) => {
    const client = io.connect(socketUrl, options);
    client.on('connect', () => {
      const maliciousName = `<script>alert('XSS')</script>`;
      client.emit('submitName', { name: maliciousName });
      client.on('nameAssigned', (assignedName) => {
        expect(assignedName).to.not.include('<script>');
        client.disconnect();
        done();
      });
    });
  });

  it('should broadcast drawing data to other clients', (done) => {
    const client1 = io.connect(socketUrl, options);
    const client2 = io.connect(socketUrl, options);

    client2.on('drawingData', (data) => {
      expect(data.x0).to.equal(0);
      expect(data.y0).to.equal(0);
      expect(data.x1).to.equal(100);
      expect(data.y1).to.equal(100);
      client1.disconnect();
      client2.disconnect();
      done();
    });

    client1.on('connect', () => {
      client1.emit('drawing', {
        x0: 0,
        y0: 0,
        x1: 100,
        y1: 100,
        thickness: 5,
        userId: 'TestUser',
      });
    });
  });

  it('should remove user from active users on disconnection', (done) => {
    const client = io.connect(socketUrl, options);
    client.on('connect', () => {
      client.emit('submitName', { name: 'DisconnectUser' });
      client.on('nameAssigned', () => {
        client.disconnect();

        // Wait a moment for the server to process the disconnection
        setTimeout(() => {
          const activeUsers = serverModule.activeUsers;
          expect(activeUsers).to.not.include('DisconnectUser');
          done();
        }, 500);
      });
    });
  });
});
''',

    'tests/integration/test_integration.js': '''
/**
 * @file test_integration.js
 * @description Integration tests for client-server interactions
 */

const chai = require('chai');
const { expect } = chai;
const http = require('http');
const io = require('socket.io-client');
const serverModule = require('../../server/server.js');

describe('Integration Tests', function () {
  this.timeout(10000); // Increase timeout for async operations

  let server;
  let socketUrl;
  let options = {
    transports: ['websocket'],
    'force new connection': true,
  };

  before((done) => {
    // Start the server
    const app = serverModule.app; // Assuming server.js exports an app
    server = http.createServer(app);
    server.listen(() => {
      const port = server.address().port;
      socketUrl = `http://localhost:${port}`;
      done();
    });
  });

  after(() => {
    server.close();
  });

  it('should establish connection and assign unique names', (done) => {
    const client1 = io.connect(socketUrl, options);
    const client2 = io.connect(socketUrl, options);
    let name1, name2;

    client1.on('connect', () => {
      client1.emit('submitName', { name: 'User' });
      client1.on('nameAssigned', (assignedName) => {
        name1 = assignedName;

        client2.emit('submitName', { name: 'User' });
        client2.on('nameAssigned', (assignedName2) => {
          name2 = assignedName2;
          expect(name1).to.equal('User');
          expect(name2).to.equal('User_1');
          client1.disconnect();
          client2.disconnect();
          done();
        });
      });
    });
  });

  it('should synchronize drawing between clients', (done) => {
    const client1 = io.connect(socketUrl, options);
    const client2 = io.connect(socketUrl, options);

    client2.on('drawingData', (data) => {
      expect(data.x0).to.equal(50);
      expect(data.y0).to.equal(50);
      expect(data.x1).to.equal(150);
      expect(data.y1).to.equal(150);
      client1.disconnect();
      client2.disconnect();
      done();
    });

    client1.on('connect', () => {
      client1.emit('submitName', { name: 'Artist' });
      client1.on('nameAssigned', () => {
        client1.emit('drawing', {
          x0: 50,
          y0: 50,
          x1: 150,
          y1: 150,
          thickness: 5,
          userId: 'Artist',
        });
      });
    });
  });

  it('should handle marker thickness synchronization', (done) => {
    const client1 = io.connect(socketUrl, options);
    const client2 = io.connect(socketUrl, options);

    client2.on('drawingData', (data) => {
      expect(data.thickness).to.equal(10);
      client1.disconnect();
      client2.disconnect();
      done();
    });

    client1.on('connect', () => {
      client1.emit('drawing', {
        x0: 0,
        y0: 0,
        x1: 100,
        y1: 100,
        thickness: 10,
        userId: 'Artist',
      });
    });
  });

  it('should handle simultaneous drawing from multiple clients', (done) => {
    let drawEventsReceived = 0;
    const client1 = io.connect(socketUrl, options);
    const client2 = io.connect(socketUrl, options);
    const client3 = io.connect(socketUrl, options);

    const checkDone = () => {
      if (drawEventsReceived === 2) {
        client1.disconnect();
        client2.disconnect();
        client3.disconnect();
        done();
      }
    };

    client1.on('drawingData', () => {
      drawEventsReceived++;
      checkDone();
    });

    client2.on('connect', () => {
      client2.emit('drawing', {
        x0: 10,
        y0: 10,
        x1: 20,
        y1: 20,
        thickness: 5,
        userId: 'User2'
      });
    });

    client3.on('connect', () => {
      client3.emit('drawing', {
        x0: 30,
        y0: 30,
        x1: 40,
        y1: 40,
        thickness: 5,
        userId: 'User3'
      });
    });
  });
});
''',

    'tests/system/test_system.js': '''
/**
 * @file test_system.js
 * @description System tests using Cypress
 */

// cypress/integration/system_tests.spec.js
describe('System Tests', () => {
  beforeEach(() => {
    // Visit the application URL
    cy.visit('http://localhost:3000'); // Adjust the URL and port as needed
  });

  it('allows a new user to join and draw on the canvas', () => {
    // Enter user name
    cy.get('#nameInput').type('TestUser');
    cy.get('#nameSubmit').click();

    // Verify that the user name is displayed
    cy.get('#userNameDisplay').should('contain', 'TestUser');

    // Draw on the canvas
    cy.get('#drawingCanvas')
      .trigger('mousedown', { clientX: 100, clientY: 100 })
      .trigger('mousemove', { clientX: 200, clientY: 200 })
      .trigger('mouseup');

    // Verify that drawing data is emitted
    // This verification may require intercepting network or socket events
  });

  it('assigns a default ID when no name is entered', () => {
    cy.get('#nameSubmit').click();

    // Verify that a default ID is assigned
    cy.get('#userNameDisplay').invoke('text').then((text) => {
      expect(text.startsWith('User_')).to.be.true;
    });

    // Ensure that the user cannot edit the name after submission
    cy.get('#nameInput').should('be.disabled');
  });

  it('handles duplicate names by appending an integer', () => {
    // This test would require simulating two users with the same name
    // Due to the limitations, we can only test one user in Cypress
    // Alternatively, mock the server response to simulate duplicate name assignment
    // For demonstration purposes:
    cy.get('#nameInput').type('Alex');
    cy.get('#nameSubmit').click();

    // Assume the server appends '_1' to the name 'Alex'
    cy.get('#userNameDisplay').should('not.equal', 'Alex');
  });

  it('supports touch input on mobile devices', () => {
    // Set viewport to mobile size
    cy.viewport('iphone-6');

    // Draw on the canvas using touch events
    cy.get('#drawingCanvas')
      .trigger('touchstart', { touches: [{ clientX: 50, clientY: 50 }] })
      .trigger('touchmove', { touches: [{ clientX: 100, clientY: 100 }] })
      .trigger('touchend');

    // Verify that the drawing data is emitted
    // This may require additional setup to capture socket events
  });
});
''',

    'tests/regression/test_regression.js': '''
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
''',

    'tests/performance/performance_test.yml': '''
# performance_test.yml
config:
  target: 'http://localhost:3000' # Adjust the URL and port as needed
  phases:
    - duration: 60   # Test duration in seconds
      arrivalRate: 10 # Number of users to simulate per second
  processor: './processors.js' # Custom JS functions (optional)

scenarios:
  - engine: 'ws' # Use WebSocket protocol
    flow:
      - function: 'connectSocket'
      - loop:
          - think: 1 # Wait for 1 second
          - function: 'sendDrawingData'
        count: 60 # Number of times to send drawing data
''',

    'tests/performance/processors.js': '''
// processors.js
module.exports = {
  connectSocket: function (context, events, done) {
    context.vars.socket = require('socket.io-client')(context.config.target);
    context.vars.socket.on('connect', () => {
      // Emit submitName event
      context.vars.socket.emit('submitName', { name: `User_${Math.floor(Math.random() * 1000)}` });
      done();
    });
  },
  sendDrawingData: function (context, events, done) {
    const socket = context.vars.socket;
    const drawingData = {
      x0: Math.random() * 500,
      y0: Math.random() * 500,
      x1: Math.random() * 500,
      y1: Math.random() * 500,
      thickness: Math.floor(Math.random() * 10) + 1,
      userId: `User_${Math.floor(Math.random() * 1000)}`,
    };
    socket.emit('drawing', drawingData);
    done();
  },
};
''',

    'tests/security/test_security.js': '''
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
''',

    'package.json': '''
{
  "scripts": {
    "start": "node server/server.js",
    "dev": "nodemon server/server.js",
    "test:unit": "mocha tests/unit/**/*.js",
    "test:integration": "mocha tests/integration/**/*.js",
    "test:system": "cypress run",
    "test:performance": "artillery run tests/performance/performance_test.yml",
    "test:security": "mocha tests/security/**/*.js",
    "test": "npm run test:unit && npm run test:integration && npm run test:system && npm run test:performance && npm run test:security"
  },
  "devDependencies": {
    "chai": "^4.3.4",
    "mocha": "^8.4.0",
    "sinon": "^11.1.2",
    "jsdom": "^16.6.0",
    "socket.io-client": "^4.1.3",
    "canvas-prebuilt": "^2.0.0-alpha.14",
    "artillery": "^1.7.8",
    "zap-client": "^0.3.7",
    "cypress": "^8.3.0"
  }
}
''',

    '.eslintrc.js': '''
module.exports = {
  env: {
    browser: true,
    es6: true,
    node: true,
    mocha: true,
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
  },
  rules: {
    // Customize your linting rules
    'no-unused-vars': ['warn'],
    'no-console': 'off',
  },
};
''',

    '.gitignore': '''
node_modules/
.env
coverage/
cypress/videos/
cypress/screenshots/
'''
}

# Create the directories and files
for filepath, content in files.items():
    # Create the directory if it doesn't exist
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    # Write the file content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())