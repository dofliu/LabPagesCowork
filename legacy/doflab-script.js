/**
 * =================================================================
 * DOF Lab - Global JavaScript
 * =================================================================
 * This file contains shared scripts for the entire website.
 *
 * Sections:
 * 1. General Setup & Smooth Scrolling
 * 2. Header Effects
 * 3. Intersection Observer for Animations
 * 4. Mobile Navigation (Hamburger Menu)
 * 5. Back to Top Button
 * =================================================================
 */

document.addEventListener('DOMContentLoaded', () => {

    /**
     * 1. General Setup & Smooth Scrolling
     * -----------------------------------------------------------------
     * Handles smooth scrolling for anchor links.
     */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const target = document.querySelector(targetId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    /**
     * 2. Header Effects
     * -----------------------------------------------------------------
     * Changes header background on scroll.
     */
    const header = document.querySelector('header');
    if (header) {
        window.addEventListener('scroll', () => {
            header.style.background = (window.scrollY > 50) ? 'rgba(255, 255, 255, 0.98)' : 'rgba(255, 255, 255, 0.95)';
        });
    }

    /**
     * 3. Intersection Observer for Animations
     * -----------------------------------------------------------------
     * Applies a fade-in-up animation to elements as they enter the viewport.
     * Add the class "animate-on-scroll" to any element you want to animate.
     */
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                obs.unobserve(entry.target); // Stop observing after animation
            }
        });
    }, observerOptions);

    // Find all elements with the class 'animate-on-scroll' and observe them
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });

    /**
     * 4. Mobile Navigation (Hamburger Menu)
     * -----------------------------------------------------------------
     * Toggles the mobile navigation menu.
     */
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        // Create and add close button
        const closeButton = document.createElement('li');
        closeButton.innerHTML = `<a href="#" class="close-menu" aria-label="關閉導覽選單"><i class="fas fa-times"></i></a>`;
        navLinks.prepend(closeButton);

        const toggleNav = () => {
            document.body.classList.toggle('mobile-nav-open');
        };

        hamburger.addEventListener('click', toggleNav);
        closeButton.addEventListener('click', (e) => {
            e.preventDefault();
            toggleNav();
        });

        // Close menu when a link is clicked
        navLinks.addEventListener('click', (e) => {
            if (e.target.tagName === 'A' && !e.target.classList.contains('close-menu')) {
                document.body.classList.remove('mobile-nav-open');
            }
        });
    }

    /**
     * 5. Back to Top Button
     * -----------------------------------------------------------------
     * Creates and manages the "Back to Top" button.
     */
    const backToTopButton = document.createElement('a');
    backToTopButton.setAttribute('href', '#');
    backToTopButton.id = 'back-to-top-btn';
    backToTopButton.title = '回到頂部';
    backToTopButton.innerHTML = `<i class="fas fa-arrow-up"></i>`;
    document.body.appendChild(backToTopButton);

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });

    backToTopButton.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

});