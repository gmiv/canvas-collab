// server/server.js
const express = require('express');
const app = express();
const http = require('http').createServer(app);
const path = require('path');
const io = require('socket.io')(http);
const sanitizeHtml = require('sanitize-html');

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, '..', 'public')));

// Active users map
const activeUsers = new Map();

// Function to generate a small ID
function generateSmallId() {
    return `User_${Math.floor(Math.random() * 1000)}`;
}

// Handle Socket.io connections
io.on('connection', (socket) => {
    console.log('A user connected');

    // Listen for name submission
    socket.on('submitName', ({ name }) => {
        let sanitizedName = sanitizeHtml(name, { allowedTags: [], allowedAttributes: {} });

        // If no name provided, assign a small ID
        if (!sanitizedName) {
            sanitizedName = generateSmallId();
        }

        // Handle duplicate names
        let assignedName = sanitizedName;
        let counter = 1;
        while (activeUsers.has(assignedName)) {
            assignedName = `${sanitizedName}_${counter}`;
            counter++;
        }

        // Store the assigned name with the socket ID
        activeUsers.set(assignedName, socket.id);
        socket.userName = assignedName;

        // Send the assigned name back to the client
        socket.emit('nameAssigned', assignedName);
    });

    // Listen for drawing data
    socket.on('drawing', (data) => {
        // Validate data using JSON schema or simple checks
        if (typeof data !== 'object') return;
        // Add server-side validation if necessary

        // Broadcast drawing data to all other clients
        socket.broadcast.emit('drawingData', data);
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('A user disconnected');
        if (socket.userName) {
            activeUsers.delete(socket.userName);
        }
    });
});

// Start the server
const PORT = process.env.PORT || 3000;
http.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

// Export for testing purposes
module.exports = { app, activeUsers };
