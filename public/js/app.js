// public/js/app.js
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
