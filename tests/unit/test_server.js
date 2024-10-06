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