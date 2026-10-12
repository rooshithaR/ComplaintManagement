// Smart Complaint Management System - Interactive Frontend Logic

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Navigation Toggle
    const navToggle = document.getElementById('nav-toggle-btn');
    const navMenu = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('open');
            const icon = navToggle.querySelector('i');
            if (icon) {
                if (navMenu.classList.contains('open')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-xmark');
                } else {
                    icon.classList.remove('fa-xmark');
                    icon.classList.add('fa-bars');
                }
            }
        });
    }

    // 2. Auto-dismiss flash notifications after 6 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 400);
        }, 6000);
    });

    // 3. Status Update Confirmation Feedback
    const statusForms = document.querySelectorAll('.status-update-inline-form');
    statusForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const select = form.querySelector('select[name="status"]');
            const statusName = select ? select.value : '';
            const idInput = form.querySelector('input[name="complaint_id"]');
            const complaintId = idInput ? idInput.value : '';

            // Soft confirmation for critical stages
            if (statusName === 'Closed') {
                if (!confirm(`Are you sure you want to mark Complaint #${complaintId} as Closed?`)) {
                    e.preventDefault();
                }
            }
        });
    });

    // 4. Client-side quick filter / search in admin table if search input exists
    const adminTable = document.getElementById('complaintsTable');
    if (adminTable) {
        // Highlight updated row if URL has anchor or recently updated
        const urlParams = new URLSearchParams(window.location.search);
        const highlightedId = urlParams.get('highlight');
        if (highlightedId) {
            const targetRow = document.querySelector(`tr[data-id="${highlightedId}"]`);
            if (targetRow) {
                targetRow.style.backgroundColor = '#fef9c3';
                targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    // 5. Form submission loading indicator
    const complaintForm = document.getElementById('complaintForm');
    if (complaintForm) {
        complaintForm.addEventListener('submit', function () {
            const submitBtn = document.getElementById('btn-submit-complaint');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
            }
        });
    }
});
