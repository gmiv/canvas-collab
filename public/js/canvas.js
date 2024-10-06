// public/js/canvas.js
// Get canvas element and context
const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');

// Adjust canvas size to fill the window
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

// Variables for drawing
let isDrawing = false;
let lastX = 0;
let lastY = 0;
let thickness = 5;

// Get thickness control element
const thicknessRange = document.getElementById('thicknessRange');

// Update thickness when the user adjusts the slider
thicknessRange.addEventListener('input', () => {
    thickness = thicknessRange.value;
});

// Set up drawing functions
function startDrawing(e) {
    isDrawing = true;
    [lastX, lastY] = getCoordinates(e);
}

function draw(e) {
    if (!isDrawing) return;
    const [x, y] = getCoordinates(e);
    ctx.lineWidth = thickness;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.closePath();

    // Emit drawing data
    socket.emit('drawing', {
        x0: lastX,
        y0: lastY,
        x1: x,
        y1: y,
        thickness: thickness,
        userId: window.userId || `User_${Math.floor(Math.random() * 1000)}`,
    });

    [lastX, lastY] = [x, y];
}

function stopDrawing() {
    isDrawing = false;
}

function getCoordinates(e) {
    let x, y;
    if (e.touches) {
        x = e.touches[0].clientX || e.changedTouches[0].clientX;
        y = e.touches[0].clientY || e.changedTouches[0].clientY;
    } else {
        x = e.offsetX;
        y = e.offsetY;
    }
    return [x, y];
}

// Event listeners for mouse events
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseout', stopDrawing);

// Event listeners for touch events
canvas.addEventListener('touchstart', (e) => {
    e.preventDefault(); // Prevent scrolling
    startDrawing(e);
});
canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    draw(e);
});
canvas.addEventListener('touchend', (e) => {
    e.preventDefault();
    stopDrawing();
});

// Expose variables and functions for testing
if (typeof module !== 'undefined') {
    module.exports = {
        canvas,
        ctx,
        isDrawing,
        lastX,
        lastY,
        startDrawing,
        draw,
        stopDrawing,
        thickness,
        setThickness: (value) => {
            thickness = value;
            ctx.lineWidth = thickness;
        },
    };
}
