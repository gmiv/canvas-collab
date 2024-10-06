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