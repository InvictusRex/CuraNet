// Common JavaScript functionality across all pages

// Theme toggle functionality
function toggleTheme() {
  const body = document.body;
  if (body.hasAttribute("data-theme")) {
    body.removeAttribute("data-theme");
    localStorage.setItem("theme", "dark");
  } else {
    body.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "light");
  }
}

// Initialize theme from localStorage
function initializeTheme() {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.setAttribute("data-theme", "dark");
  }
}

// Modal functionality
function initializeModals() {
  // Open modal functionality
  document.querySelectorAll("[data-modal]").forEach((button) => {
    button.addEventListener("click", () => {
      const modalId = button.getAttribute("data-modal");
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.style.display = "flex";
      }
    });
  });

  // Close modal functionality
  document.querySelectorAll(".close-modal").forEach((button) => {
    button.addEventListener("click", () => {
      button.closest(".modal").style.display = "none";
    });
  });

  // Close modal when clicking outside
  window.addEventListener("click", (event) => {
    if (event.target.classList.contains("modal")) {
      event.target.style.display = "none";
    }
  });
}

// Navigation active state management
function setActiveNavItem() {
  const currentPage = window.location.pathname.split('/').pop();
  const navLinks = document.querySelectorAll('.nav-menu a');
  
  navLinks.forEach(link => {
    link.classList.remove('active');
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === '#')) {
      link.classList.add('active');
    }
  });
}

// Format date and time consistently
function formatDateTime(dateTimeString) {
  const date = new Date(dateTimeString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Show loading state for buttons
function setButtonLoading(button, isLoading, originalText = 'Submit') {
  if (isLoading) {
    button.disabled = true;
    button.textContent = 'Loading...';
  } else {
    button.disabled = false;
    button.textContent = originalText;
  }
}

// Show notifications/alerts
function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  // Style the notification
  Object.assign(notification.style, {
    position: 'fixed',
    top: '20px',
    right: '20px',
    padding: '1rem 1.5rem',
    borderRadius: '8px',
    color: 'white',
    fontWeight: '600',
    zIndex: '9999',
    opacity: '0',
    transform: 'translateY(-20px)',
    transition: 'all 0.3s ease'
  });

  // Set background color based on type
  const colors = {
    success: '#4caf50',
    error: '#f44336',
    warning: '#ffc107',
    info: '#2196f3'
  };
  notification.style.backgroundColor = colors[type] || colors.info;

  // Add to DOM
  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.style.opacity = '1';
    notification.style.transform = 'translateY(0)';
  }, 100);

  // Remove after 5 seconds
  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(-20px)';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 5000);
}

// Validate form inputs
function validateForm(formElement) {
  const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
  let isValid = true;

  inputs.forEach(input => {
    if (!input.value.trim()) {
      input.style.borderColor = 'var(--danger-color)';
      isValid = false;
    } else {
      input.style.borderColor = 'var(--border-color)';
    }
  });

  return isValid;
}

// Handle API errors consistently
function handleApiError(error, defaultMessage = 'An error occurred') {
  console.error('API Error:', error);
  
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.detail || error.response.data?.message || defaultMessage;
    showNotification(message, 'error');
  } else if (error.request) {
    // Network error
    showNotification('Network error. Please check your connection.', 'error');
  } else {
    // Other error
    showNotification(defaultMessage, 'error');
  }
}

// Check authentication status
function checkAuth() {
  const username = localStorage.getItem('username');
  const userType = localStorage.getItem('user_type');
  
  if (!username || !userType) {
    window.location.href = '/';
    return false;
  }
  
  return { username, userType };
}

// Logout functionality
function logout() {
  localStorage.clear();
  window.location.href = '/';
}

// Enhanced navigation management
function updateNavigationState() {
  const currentPath = window.location.pathname;
  const currentPage = currentPath.split('/').pop() || 'index.html';
  
  // Update active navigation state
  document.querySelectorAll('.nav-menu a').forEach(link => {
    link.classList.remove('active');
    const href = link.getAttribute('href');
    if (href) {
      const linkPage = href.split('/').pop();
      if (linkPage === currentPage || 
          (currentPage === 'index.html' && href === '/') ||
          (currentPage === '' && href === '/')) {
        link.classList.add('active');
      }
    }
  });
}

// Enhanced user info loading
async function loadUserInfo() {
  const auth = checkAuth();
  if (!auth) return;

  try {
    let endpoint = '';
    if (auth.userType === 'doctor') {
      endpoint = `/doctor/dashboard-info/${auth.username}`;
    } else if (auth.userType === 'patient') {
      endpoint = `/patient/dashboard-info/${auth.username}`;
    } else {
      return;
    }

    const response = await fetch(endpoint);
    if (!response.ok) throw new Error('Failed to fetch user info');
    
    const userData = await response.json();
    
    // Update user info in sidebar
    if (window.layoutManager) {
      window.layoutManager.updateUserInfo({
        name: userData.name,
        id: userData.patient_id || userData.doctor_id
      });
    }
    
    return userData;
  } catch (error) {
    console.error('Error loading user info:', error);
  }
}

// Initialize common functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  initializeTheme();
  initializeModals();
  updateNavigationState();
  
  // Load user info if on a dashboard page
  if (document.querySelector('.sidebar')) {
    loadUserInfo();
  }
  
  // Add logout functionality to logout links
  document.querySelectorAll('a[href="/"], a[href="index.html"]').forEach(link => {
    if (link.textContent.toLowerCase().includes('logout')) {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        logout();
      });
    }
  });
  
  // Add page transition effects
  document.body.classList.add('page-loaded');
});

// Export functions for use in other scripts
window.CuraNetCommon = {
  toggleTheme,
  initializeTheme,
  initializeModals,
  setActiveNavItem,
  formatDateTime,
  setButtonLoading,
  showNotification,
  validateForm,
  handleApiError,
  checkAuth,
  logout,
  updateNavigationState,
  loadUserInfo
};