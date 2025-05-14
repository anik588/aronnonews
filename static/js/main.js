document.addEventListener('DOMContentLoaded', () => {
    // Dropdown handling for desktop view
    const dropdownItems = document.querySelectorAll('.custom-nav-item.dropdown');

    dropdownItems.forEach(item => {
        const dropdownToggle = item.querySelector('.dropdown-toggle');
        const dropdownMenu = item.querySelector('.dropdown-menu');

        // Show dropdown on hover for desktop
        item.addEventListener('mouseenter', () => {
            dropdownMenu.classList.add('show');
        });

        item.addEventListener('mouseleave', () => {
            dropdownMenu.classList.remove('show');
        });

        // Toggle dropdown on click
        dropdownToggle.addEventListener('click', (event) => {
            event.preventDefault();
            dropdownMenu.classList.toggle('show');
        });
    });

    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.custom-toggler');
    const mobileMenu = document.getElementById('navbarNav');

    mobileMenuButton.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevent the click from propagating to the window
        const isExpanded = mobileMenu.classList.contains('show');
        mobileMenu.classList.toggle('show', !isExpanded);
        mobileMenu.classList.toggle('expand', !isExpanded);
    });

    // Close dropdowns and mobile menu on outside click
    window.addEventListener('click', (event) => {
        const isDropdownClick = event.target.closest('.custom-nav-item.dropdown');
        const isMobileMenuClick = event.target.closest('.custom-toggler') || event.target.closest('#navbarNav');

        if (!isDropdownClick && !isMobileMenuClick) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });

            if (mobileMenu.classList.contains('show')) {
                mobileMenu.classList.remove('show');
                mobileMenu.classList.remove('expand');
            }
        }
    });

    // Prevent clicks inside the mobile menu from closing it
    mobileMenu.addEventListener('click', (event) => {
        event.stopPropagation();
    });
});

// News Share Link
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        const notification = document.getElementById('linkCopiedNotification');
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 2000);
    }).catch(err => console.error('Failed to copy text: ', err));
}

// Breaking or Most Breaking Section Toggle
function breaking_or_mostread_toggle(section) {
    const breakingNews = document.getElementById('breaking_or_mostread_breaking_news');
    const mostReadNews = document.getElementById('breaking_or_mostread_mostread_news');
    const activeBtn = document.querySelector('.breaking-or-mostread-toggle-btn.active');
    const targetBtn = document.querySelector(`button[onclick="breaking_or_mostread_toggle('${section}')"]`);

    breakingNews.classList.remove('active');
    mostReadNews.classList.remove('active');
    activeBtn?.classList.remove('active');

    if (section === 'breaking') {
        breakingNews.classList.add('active');
    } else {
        mostReadNews.classList.add('active');
    }
    targetBtn.classList.add('active');
}
