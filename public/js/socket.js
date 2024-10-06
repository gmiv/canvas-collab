// public/js/socket.js
// Listen for drawing data from server
socket.on('drawingData', (data) => {
    drawOnCanvas(data);
});

// Function to draw on the canvas based on received data
function drawOnCanvas(data) {
    const { x0, y0, x1, y1, thickness, userId } = data;
    ctx.lineWidth = thickness;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
    ctx.closePath();
}
