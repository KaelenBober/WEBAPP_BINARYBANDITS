const movableImage = document.getElementById('movableImage');
let posX = window.innerWidth / 2;
let posY = window.innerHeight / 2;
const moveSpeed = 10;  // Adjust movement speed

// Set target zone coordinates
const targetZone = { x: 551, y:30, width: 168, height: 130};

// Initialize movement flags for keys
let movingUp = false;
let movingDown = false;
let movingLeft = false;
let movingRight = false;

// Add a flag to track if the user is in the target zone
let inTargetZone = false;

// Listen for key presses and move the character
document.addEventListener('keydown', function(event) {
    console.log(`Key pressed: ${event.key}`);  // Debug line
    if (event.key === 'w') movingUp = true;
    if (event.key === 's') movingDown = true;
    if (event.key === 'a') movingLeft = true;
    if (event.key === 'd') movingRight = true;

    if (inTargetZone) {
        showOverlay();
    }

    if (!inTargetZone) {
        hideOverlay();
    }

    moveCharacter();
});


document.addEventListener('keyup', function(event) {
    if (event.key === 'w') movingUp = false;
    if (event.key === 's') movingDown = false;
    if (event.key === 'a') movingLeft = false;
    if (event.key === 'd') movingRight = false;
});

function moveCharacter() {
    let moveX = 0;
    let moveY = 0;

    if (movingUp) moveY = -moveSpeed;
    if (movingDown) moveY = moveSpeed;
    if (movingLeft) moveX = -moveSpeed;
    if (movingRight) moveX = moveSpeed;

    posX += moveX;
    posY += moveY;

    movableImage.style.left = `${posX}px`;
    movableImage.style.top = `${posY}px`;

    // Check if character is in the target zone
    inTargetZone = (
        posX >= targetZone.x &&
        posX <= targetZone.x + targetZone.width &&
        posY >= targetZone.y &&
        posY <= targetZone.y + targetZone.height
    );
}

function showOverlay() {
    console.log("Overlay triggered"); // Debug line
    const overlay = document.getElementById('overlay');
    overlay.style.display = 'flex';
}

// Function to hide the overlay
function hideOverlay() {
    const overlay = document.getElementById('overlay');
    overlay.style.display = 'none';
}

// Attach event listener to the exit button
document.getElementById('exitButton').addEventListener('click', hideOverlay);

