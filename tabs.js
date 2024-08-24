function animateItems(tabId) {
    const items = document.querySelectorAll(`${tabId} .game-item`);
    items.forEach((item, index) => {
        item.style.animation = `fallIn 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94) ${index * 0.1}s forwards`;
    });
}

document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('nav a').forEach(navLink => navLink.classList.remove('active'));
        const targetTab = document.querySelector(this.getAttribute('href'));
        targetTab.classList.add('active');
        this.classList.add('active');

        if (targetTab.id === 'games' || targetTab.id === 'other') {
            animateItems(`#${targetTab.id}`);
        }
    });
});

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