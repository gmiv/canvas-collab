/**
 * @file test_canvas.js
 * @description Unit tests for canvas.js
 */

const { JSDOM } = require('jsdom');
const { expect } = require('chai');
const sinon = require('sinon');
const { createCanvas } = require('canvas');

// Mock the DOM and Canvas
const dom = new JSDOM(`<!DOCTYPE html><html><body><canvas id="drawingCanvas"></canvas></body></html>`, {
  pretendToBeVisual: true,
});
global.window = dom.window;
global.document = dom.window.document;

// Attach the canvas to the window
global.window.HTMLCanvasElement.prototype.getContext = function () {
  return {
    // Mocked context methods
    beginPath: sinon.spy(),
    moveTo: sinon.spy(),
    lineTo: sinon.spy(),
    stroke: sinon.spy(),
    closePath: sinon.spy(),
    lineWidth: 1,
    strokeStyle: '#000000',
    lineCap: 'butt',
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