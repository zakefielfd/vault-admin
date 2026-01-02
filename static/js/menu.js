// static/js/menu.js
document.addEventListener('DOMContentLoaded', function() {
    const items = document.querySelectorAll('.menu-item');
    let current = 0;

    function updateHighlight() {
        items.forEach((item, i) => {
            if (i === current) {
                item.classList.add('selected');
                item.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            current = (current + 1) % items.length;
            updateHighlight();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            current = (current - 1 + items.length) % items.length;
            updateHighlight();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            items[current].querySelector('button, input[type="submit"], a').click();
        }
    });

    // Highlight inicial
    if (items.length > 0) {
        updateHighlight();
    }

    // Ocultar cursor del ratón para inmersión total
    document.body.style.cursor = 'none';
});
