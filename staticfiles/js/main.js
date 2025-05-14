//-----Navbar-----Start--
document.addEventListener('DOMContentLoaded', () => {
    // Desktop dropdown handling
    const dropdownItems = document.querySelectorAll('.custom-nav-item.dropdown');

    dropdownItems.forEach(item => {
        const dropdownToggle = item.querySelector('.dropdown-toggle');
        const dropdownMenu = item.querySelector('.dropdown-menu');

        // Show dropdown on hover
        item.addEventListener('mouseenter', () => {
            dropdownMenu.classList.add('show'); // Show on hover
        });

        // Hide dropdown on mouse leave
        item.addEventListener('mouseleave', () => {
            dropdownMenu.classList.remove('show'); // Hide on mouse leave
        });

        // Click to hold the dropdown open
        dropdownToggle.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent default anchor action
            dropdownMenu.classList.toggle('show'); // Toggle dropdown visibility
        });
    });

    // Mobile menu handling
    const mobileMenuButton = document.querySelector('.custom-toggler');
    const mobileMenu = document.getElementById('navbarNav');

    mobileMenuButton.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevents immediate closing after opening
        mobileMenu.classList.toggle('show'); // Toggle mobile menu visibility
    });

    // Close dropdowns and mobile menu when clicking outside
    window.addEventListener('click', (event) => {
        const isDropdownClick = event.target.closest('.custom-nav-item.dropdown');
        const isMobileMenuClick = event.target.closest('.custom-toggler') || event.target.closest('#navbarNav');

        if (!isDropdownClick && !isMobileMenuClick) {
            // Hide all dropdown menus
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });

            // Hide the mobile menu
            if (mobileMenu.classList.contains('show')) {
                mobileMenu.classList.remove('show');
            }
        }
    });

    // Prevent mobile menu from closing when interacting with dropdowns inside it
    mobileMenu.addEventListener('click', (event) => {
        event.stopPropagation();
    });
});


//-----Navbar-----END--


/// News Share Link
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show notification
        const notification = document.getElementById('linkCopiedNotification');
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 2000);
    }).catch(err => console.error('Failed to copy text: ', err));
}


// News Details AD Gap
// Function to copy URL to clipboard

//breaking-or-most-breaking-section
function breaking_or_mostread_toggle(section) {
    const breakingNews = document.getElementById('breaking_or_mostread_breaking_news');
    const mostReadNews = document.getElementById('breaking_or_mostread_mostread_news');
    const breakingBtn = document.querySelector('.breaking-or-mostread-toggle-btn.active');
    const mostReadBtn = document.querySelector(`button[onclick="breaking_or_mostread_toggle('${section}')"]`);

    // Hide both sections and reset button states
    breakingNews.classList.remove('active');
    mostReadNews.classList.remove('active');
    breakingBtn.classList.remove('active');

    // Show the selected section and activate the button
    if (section === 'breaking') {
        breakingNews.classList.add('active');
    } else {
        mostReadNews.classList.add('active');
    }
    mostReadBtn.classList.add('active');
}





//////////    search Function mobile END
