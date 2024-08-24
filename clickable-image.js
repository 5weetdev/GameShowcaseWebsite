class ClickableImage extends HTMLImageElement {
    constructor() {
        super();
        this.style.cursor = 'pointer'; 
        this.addEventListener('click', this.openInNewTab);
    }

    openInNewTab() {
        const imageUrl = this.src;
        window.open(imageUrl, '_blank');
    }
}

// Define the custom element
customElements.define('clickable-image', ClickableImage, { extends: 'img' });
