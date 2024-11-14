const movableImage = document.getElementById('movableImage');
let posX = window.innerWidth / 2;
let posY = window.innerHeight / 2;
const moveSpeed = 10;  // Adjust movement speed

// Initialize movement flags for keys
let movingUp = false;
let movingDown = false;
let movingLeft = false;
let movingRight = false;

// Listen for key presses and move the character accordingly
document.addEventListener('keydown', function(event) {
    if (event.key === 'w') {
        movingUp = true;
    }
    if (event.key === 's') {
        movingDown = true;
    }
    if (event.key === 'a') {
        movingLeft = true;
    }
    if (event.key === 'd') {
        movingRight = true;
    }

    moveCharacter();
});

// Listen for key releases to stop movement
document.addEventListener('keyup', function(event) {
    if (event.key === 'w') {
        movingUp = false;
    }
    if (event.key === 's') {
        movingDown = false;
    }
    if (event.key === 'a') {
        movingLeft = false;
    }
    if (event.key === 'd') {
        movingRight = false;
    }

    moveCharacter();
});

function moveCharacter() {
    let moveX = 0;
    let moveY = 0;

    // Combine the horizontal and vertical movement for diagonal
    if (movingUp) {
        moveY = -moveSpeed;  // Move up
    }
    if (movingDown) {
        moveY = moveSpeed;  // Move down
    }
    if (movingLeft) {
        moveX = -moveSpeed;  // Move left
    }
    if (movingRight) {
        moveX = moveSpeed;  // Move right
    }

    // Update position based on movement flags
    posX += moveX;
    posY += moveY;

    // Update the position of the image
    movableImage.style.left = `${posX}px`;
    movableImage.style.top = `${posY}px`;
}
