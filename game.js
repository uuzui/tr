const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game constants
const TILE_SIZE = 20;
const ROWS = 20;
const COLS = 20;

// Set canvas dimensions
canvas.width = COLS * TILE_SIZE;
canvas.height = ROWS * TILE_SIZE;

// Player object
const player = {
    x: 10 * TILE_SIZE,
    y: 10 * TILE_SIZE,
    width: TILE_SIZE,
    height: TILE_SIZE,
    color: '#fff'
};

function drawBackground() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawPlayer() {
    ctx.fillStyle = player.color;
    ctx.fillRect(player.x, player.y, player.width, player.height);
}

// Game loop
function gameLoop() {
    // Update game state

    // Render game
    drawBackground();
    drawPlayer();

    requestAnimationFrame(gameLoop);
}

// Keyboard input
document.addEventListener('keydown', (e) => {
    switch (e.key.toLowerCase()) {
        case 'w':
            if (player.y > 0) {
                player.y -= TILE_SIZE;
            }
            break;
        case 'a':
            if (player.x > 0) {
                player.x -= TILE_SIZE;
            }
            break;
        case 's':
            if (player.y < canvas.height - player.height) {
                player.y += TILE_SIZE;
            }
            break;
        case 'd':
            if (player.x < canvas.width - player.width) {
                player.x += TILE_SIZE;
            }
            break;
    }
});

// Start the game loop
gameLoop();
