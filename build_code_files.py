
import os

# Define the project structure and file contents
project_structure = {
    'public': {
        'index.html': '''<!-- public/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Realtime Collaborative Whiteboard</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <!-- Name Input Modal -->
    <div id="nameModal" class="modal">
        <div class="modal-content">
            <h2>Enter Your Name</h2>
            <input type="text" id="nameInput" placeholder="Your Name">
            <button id="nameSubmit">Submit</button>
        </div>
    </div>
    <!-- User Name Display -->
    <div id="userNameDisplay"></div>
    <!-- Marker Thickness Control -->
    <div id="controls">
        <label for="thicknessRange">Marker Thickness:</label>
        <input type="range" id="thicknessRange" min="1" max="20" value="5">
    </div>
    <!-- Canvas Element -->
    <canvas id="drawingCanvas"></canvas>
    <!-- Client-side Scripts -->
    <script src="/socket.io/socket.io.js"></script>
    <script src="js/app.js"></script>
    <script src="js/canvas.js"></script>
    <script src="js/socket.js"></script>
</body>
</html>
''',
        'css': {
            'styles.css': '''/* public/css/styles.css */
/* Style for the canvas to fill the entire viewport */
#drawingCanvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    cursor: crosshair;
}

/* Style for the name modal */
.modal {
    display: none; /* Hidden by default */
    position: fixed; /* Stay in place */
    z-index: 1; /* Sit on top */
    left: 0;
    top: 0;
    width: 100%; /* Full width */
    height: 100%; /* Full height */
    overflow: auto; /* Enable scroll if needed */
    background-color: rgba(0, 0, 0, 0.5); /* Black w/ opacity */
}

.modal-content {
    background-color: #fefefe;
    margin: 15% auto; /* Center it vertically and horizontally */
    padding: 20px;
    border: 1px solid #888;
    width: 300px; /* Could be more or less, depending on screen size */
    text-align: center;
}

.modal-content h2 {
    margin-top: 0;
}

#nameInput {
    width: 80%;
    padding: 8px;
    margin-bottom: 10px;
}

#nameSubmit {
    padding: 8px 16px;
}

#userNameDisplay {
    position: absolute;
    top: 10px;
    right: 20px;
    font-weight: bold;
}

#controls {
    position: absolute;
    top: 10px;
    left: 20px;
    background-color: #fff;
    padding: 10px;
    border-radius: 5px;
}

#controls label {
    margin-right: 10px;
}
''',
        },
        'js': {
            'app.js': '''// public/js/app.js
// Initialize socket connection
const socket = io();

// Function to show the name prompt modal
function showNamePrompt() {
    const nameModal = document.getElementById('nameModal');
    nameModal.style.display = 'block';
    const nameSubmit = document.getElementById('nameSubmit');
    nameSubmit.addEventListener('click', submitName);
}

// Function to submit the user's name
function submitName() {
    const nameInput = document.getElementById('nameInput');
    let name = nameInput.value.trim();

    // If no name entered, assign a small ID
    if (name === '') {
        name = `User_${Math.floor(Math.random() * 1000)}`;
    }

    // Disable name input to prevent changes
    nameInput.disabled = true;

    // Emit the name to the server
    socket.emit('submitName', { name });

    // Hide the modal
    const nameModal = document.getElementById('nameModal');
    nameModal.style.display = 'none';
}

// Listen for assigned name from server
socket.on('nameAssigned', (assignedName) => {
    const userNameDisplay = document.getElementById('userNameDisplay');
    userNameDisplay.textContent = assignedName;
    window.userId = assignedName;
});

// On page load
window.addEventListener('load', () => {
    showNamePrompt();
});
''',
            'canvas.js': '''// public/js/canvas.js
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
''',
            'socket.js': '''// public/js/socket.js
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
''',
        },
    },
    'server': {
        'server.js': '''// server/server.js
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
''',
    },
    'tests': {
        # Tests directory (empty or filled as needed)
    },
    'package.json': '''{
    "name": "realtime-collaborative-whiteboard",
    "version": "1.0.0",
    "description": "A super simple canvas painter in vanilla JavaScript with Socket.io over Node.js",
    "main": "server/server.js",
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
    "dependencies": {
        "express": "^4.17.1",
        "socket.io": "^4.1.3",
        "sanitize-html": "^2.3.3"
    },
    "devDependencies": {
        "chai": "^4.3.4",
        "mocha": "^8.4.0",
        "sinon": "^11.1.2",
        "jsdom": "^16.6.0",
        "socket.io-client": "^4.1.3",
        "cypress": "^8.3.0",
        "artillery": "^1.7.8",
        "zaproxy": "^0.3.7",
        "eslint": "^7.32.0",
        "eslint-plugin-mocha": "^9.0.0",
        "nodemon": "^2.0.12"
    },
    "author": "Your Name",
    "license": "MIT"
}
''',
    '.eslintrc.js': '''// .eslintrc.js
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
    '.gitignore': '''node_modules/
.env
coverage/
cypress/videos/
cypress/screenshots/
''',
    'README.md': '''# Realtime Collaborative Whiteboard

This project is a super simple canvas painter in vanilla JavaScript with Socket.io over Node.js.

## Project Structure

- **public/**: Frontend files served to clients
  - **index.html**: Main HTML file
  - **css/**
    - **styles.css**: CSS styles
  - **js/**
    - **app.js**: Main client-side JavaScript
    - **canvas.js**: Canvas drawing functionalities
    - **socket.js**: Socket.io client-side logic
- **server/**
  - **server.js**: Node.js server with Socket.io
- **tests/**: Tests directory (unit, integration, system, performance, security)
- **package.json**: Project dependencies and scripts
- **.eslintrc.js**: Linting configuration
- **.gitignore**: Git ignore file
- **README.md**: Project documentation

## Setup Instructions

1. **Install Dependencies**

   ```bash
   npm install
   ```

2. **Run the Application**

   ```bash
   npm start
   ```

3. **Access the Application**

   Open your web browser and navigate to `http://localhost:3000`.

## Testing

- **Unit Tests**

  ```bash
  npm run test:unit
  ```

- **Integration Tests**

  ```bash
  npm run test:integration
  ```

- **System Tests**

  ```bash
  npm run test:system
  ```

- **Performance Tests**

  ```bash
  npm run test:performance
  ```

- **Security Tests**

  ```bash
  npm run test:security
  ```

- **Run All Tests**

  ```bash
  npm test
  ```

## License

This project is licensed under the MIT License.
''',
}

def create_project_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # Create directory
            os.makedirs(path, exist_ok=True)
            # Recursively create subdirectories and files
            create_project_structure(path, content)
        else:
            # Write file content
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

if __name__ == '__main__':
    # Get the directory where the script is located
    base_directory = os.path.dirname(os.path.abspath(__file__))
    # Create the project structure
    create_project_structure(base_directory, project_structure)
    print('Project structure created successfully.')