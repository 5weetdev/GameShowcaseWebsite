function animateItems(tabId) {
    const items = document.querySelectorAll(`${tabId} .game-item`);
    items.forEach((item, index) => {
        item.style.animation = `fallIn 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94) ${index * 0.1}s forwards`;
    });
}

document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        switchTab(this.getAttribute('href'));
    });
});

document.querySelector('.logo-name').addEventListener('click', function() {
    switchTab('#home');
});

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('nav a').forEach(navLink => navLink.classList.remove('active'));
    
    const targetTab = document.querySelector(tabId);
    targetTab.classList.add('active');
    
    // Highlight the appropriate navigation link
    document.querySelector(`nav a[href="${tabId}"]`).classList.add('active');

    // Add animations if switching to games or other tabs
    if (tabId === '#games' || tabId === '#other') {
        animateItems(tabId);
    }
}


/*
document.addEventListener('DOMContentLoaded', () => {
    fetch('games.json')
        .then(response => response.json())
        .then(data => {
            const gameGrid = document.querySelector('#games .game-grid');
            gameGrid.innerHTML = ''; // Clear existing content

            data.games.forEach(game => {
                const gameItem = document.createElement('a');
                gameItem.className = 'game-item';
                gameItem.href = game.url;

                const imageContainer = document.createElement('div');
                imageContainer.className = 'game-image-container';

                const img = document.createElement('img');
                img.src = game.image;
                img.alt = game.title;

                const title = document.createElement('p');
                title.className = 'game-title';
                title.textContent = game.title;
                
                imageContainer.appendChild(img);
                gameItem.appendChild(imageContainer);
                gameItem.appendChild(title);
                gameGrid.appendChild(gameItem);
            });
        })
        .catch(error => console.error('Error loading games:', error));
});
*/