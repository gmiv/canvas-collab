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