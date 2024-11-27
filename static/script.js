const movableImage = document.getElementById('movableImage');
let posX = window.innerWidth / 2;
let posY = window.innerHeight / 2;
const moveSpeed = 10;  // Adjust movement speed



// Initialize movement flags for keys
let movingUp = false;
let movingDown = false;
let movingLeft = false;
let movingRight = false;


// Listen for key presses and move the character
document.addEventListener('keydown', function(event) {
    console.log(`Key pressed: ${event.key}`);  // Debug line
    if (event.key === 'w') movingUp = true;
    if (event.key === 's') movingDown = true;
    if (event.key === 'a') movingLeft = true;
    if (event.key === 'd') movingRight = true;

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

}


// Show the overlay with planet buttons
function showOverlay() {
    console.log("Overlay triggered"); // Debug line
    const overlay = document.getElementById('overlay');
    overlay.style.display = 'flex'; // Show the overlay
}

// Hide the overlay
function hideOverlay() {
    const overlay = document.getElementById('overlay');
    overlay.style.display = 'none'; // Hide the overlay
}

// Attach event listener to the overlay trigger button
document.getElementById('overlayTrigger').addEventListener('click', showOverlay);

// Navigate to the selected planet
function goToPlanet(planetName) {
    console.log(`You have selected: ${planetName}`);
    hideOverlay();  // Close the overlay when a planet is selected
    

    // Redirect based on the selected planet
    if (planetName === 'Tatooine') {
        window.location.href = '/tatooine';  // Path to the Tatooine page
    } else if (planetName === 'Hoth') {
        window.location.href = '/hoth';  // Path to the Hoth page (you can add this page similarly)
    } else if (planetName === 'Mustafar') {
        window.location.href = '/mustafar';  // Path to the Mustafar page (you can add this page similarly)
    }
}

function hideOverlay() {
    const overlay = document.getElementById('overlay');
    overlay.style.display = 'none';
}


