// Unified Layout Management for CuraNet HMS

class LayoutManager {
  constructor() {
    this.sidebar = null;
    this.sidebarToggle = null;
    this.sidebarOverlay = null;
    this.mainContent = null;
    this.isMobile = window.innerWidth <= 1024;
    
    this.init();
  }

  init() {
    this.createLayoutElements();
    this.bindEvents();
    this.handleResize();
    this.setActiveNavigation();
  }

  createLayoutElements() {
    // Create sidebar toggle button if it doesn't exist
    if (!document.querySelector('.sidebar-toggle')) {
      const toggleBtn = document.createElement('button');
      toggleBtn.className = 'sidebar-toggle';
      toggleBtn.innerHTML = '☰';
      toggleBtn.setAttribute('aria-label', 'Toggle sidebar');
      document.body.appendChild(toggleBtn);
    }

    // Create sidebar overlay for mobile
    if (!document.querySelector('.sidebar-overlay')) {
      const overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay';
      document.body.appendChild(overlay);
    }

    // Get references to elements
    this.sidebar = document.querySelector('.sidebar');
    this.sidebarToggle = document.querySelector('.sidebar-toggle');
    this.sidebarOverlay = document.querySelector('.sidebar-overlay');
    this.mainContent = document.querySelector('.main-content');

    // Add close button to sidebar if it doesn't exist
    if (this.sidebar && !this.sidebar.querySelector('.sidebar-close')) {
      const sidebarHeader = this.sidebar.querySelector('.sidebar-header') || this.createSidebarHeader();
      const closeBtn = document.createElement('button');
      closeBtn.className = 'sidebar-close';
      closeBtn.innerHTML = '×';
      closeBtn.setAttribute('aria-label', 'Close sidebar');
      sidebarHeader.appendChild(closeBtn);
    }
  }

  createSidebarHeader() {
    const header = document.createElement('div');
    header.className = 'sidebar-header';
    
    const brand = document.createElement('a');
    brand.href = '/';
    brand.className = 'sidebar-brand';
    brand.textContent = 'CuraNet HMS';
    
    header.appendChild(brand);
    
    if (this.sidebar) {
      this.sidebar.insertBefore(header, this.sidebar.firstChild);
    }
    
    return header;
  }

  bindEvents() {
    // Sidebar toggle functionality
    if (this.sidebarToggle) {
      this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
    }

    // Sidebar close button
    const sidebarClose = document.querySelector('.sidebar-close');
    if (sidebarClose) {
      sidebarClose.addEventListener('click', () => this.closeSidebar());
    }

    // Overlay click to close sidebar
    if (this.sidebarOverlay) {
      this.sidebarOverlay.addEventListener('click', () => this.closeSidebar());
    }

    // Handle window resize
    window.addEventListener('resize', () => this.handleResize());

    // Handle navigation clicks
    document.addEventListener('click', (e) => {
      if (e.target.matches('.nav-menu a')) {
        this.handleNavigation(e);
      }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isSidebarOpen()) {
        this.closeSidebar();
      }
    });
  }

  toggleSidebar() {
    if (this.sidebar) {
      const isOpen = this.isSidebarOpen();
      
      if (isOpen) {
        this.closeSidebar();
      } else {
        this.openSidebar();
      }
    }
  }

  openSidebar() {
    if (this.sidebar) {
      this.sidebar.classList.add('show');
      this.sidebar.classList.remove('collapsed');
      
      if (this.sidebarOverlay && this.isMobile) {
        this.sidebarOverlay.classList.add('show');
      }
      
      if (this.mainContent && !this.isMobile) {
        this.mainContent.classList.remove('expanded');
      }
      
      // Focus management for accessibility
      const firstNavLink = this.sidebar.querySelector('.nav-menu a');
      if (firstNavLink) {
        firstNavLink.focus();
      }
    }
  }

  closeSidebar() {
    if (this.sidebar) {
      this.sidebar.classList.remove('show');
      
      if (this.isMobile) {
        this.sidebar.classList.add('collapsed');
      }
      
      if (this.sidebarOverlay) {
        this.sidebarOverlay.classList.remove('show');
      }
      
      if (this.mainContent && this.isMobile) {
        this.mainContent.classList.add('expanded');
      }
    }
  }

  isSidebarOpen() {
    return this.sidebar && this.sidebar.classList.contains('show');
  }

  handleResize() {
    const wasMobile = this.isMobile;
    this.isMobile = window.innerWidth <= 1024;

    if (wasMobile !== this.isMobile) {
      if (this.isMobile) {
        // Switching to mobile
        this.closeSidebar();
        if (this.sidebarToggle) {
          this.sidebarToggle.style.display = 'flex';
        }
      } else {
        // Switching to desktop
        this.openSidebar();
        if (this.sidebarToggle) {
          this.sidebarToggle.style.display = 'none';
        }
        if (this.sidebarOverlay) {
          this.sidebarOverlay.classList.remove('show');
        }
      }
    }
  }

  setActiveNavigation() {
    const currentPath = window.location.pathname;
    const currentPage = currentPath.split('/').pop() || 'index.html';
    
    // Remove active class from all nav links
    document.querySelectorAll('.nav-menu a').forEach(link => {
      link.classList.remove('active');
    });

    // Set active class based on current page
    document.querySelectorAll('.nav-menu a').forEach(link => {
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

  handleNavigation(e) {
    // Add loading state to clicked navigation item
    const link = e.target;
    const originalText = link.textContent;
    
    // Don't add loading state for external links or logout
    if (link.href.includes('http') || link.textContent.toLowerCase().includes('logout')) {
      return;
    }

    link.style.opacity = '0.6';
    
    // Remove loading state after a short delay
    setTimeout(() => {
      link.style.opacity = '1';
    }, 300);

    // Close sidebar on mobile after navigation
    if (this.isMobile) {
      setTimeout(() => this.closeSidebar(), 100);
    }
  }

  // Method to update user info in sidebar
  updateUserInfo(userData) {
    const userAvatar = document.getElementById('userAvatar');
    const userName = document.getElementById('userName');
    const userId = document.getElementById('userId') || 
                   document.getElementById('patientId') || 
                   document.getElementById('doctorId');

    if (userAvatar && userData.name) {
      userAvatar.textContent = userData.name.charAt(0).toUpperCase();
    }

    if (userName && userData.name) {
      userName.textContent = userData.name;
    }

    if (userId && userData.id) {
      userId.textContent = userData.id;
    }
  }

  // Method to show/hide loading state for the entire layout
  setLayoutLoading(isLoading) {
    if (this.mainContent) {
      if (isLoading) {
        this.mainContent.classList.add('loading');
      } else {
        this.mainContent.classList.remove('loading');
      }
    }
  }

  // Method to add breadcrumb navigation
  addBreadcrumb(items) {
    const existingBreadcrumb = document.querySelector('.breadcrumb');
    if (existingBreadcrumb) {
      existingBreadcrumb.remove();
    }

    const breadcrumb = document.createElement('nav');
    breadcrumb.className = 'breadcrumb';

    items.forEach((item, index) => {
      if (index > 0) {
        const separator = document.createElement('span');
        separator.className = 'breadcrumb-separator';
        separator.textContent = '/';
        breadcrumb.appendChild(separator);
      }

      if (item.href && index < items.length - 1) {
        const link = document.createElement('a');
        link.href = item.href;
        link.textContent = item.text;
        breadcrumb.appendChild(link);
      } else {
        const span = document.createElement('span');
        span.className = 'current';
        span.textContent = item.text;
        breadcrumb.appendChild(span);
      }
    });

    const dashboardHeader = document.querySelector('.dashboard-header');
    if (dashboardHeader) {
      dashboardHeader.insertBefore(breadcrumb, dashboardHeader.firstChild);
    }
  }
}

// Initialize layout manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.layoutManager = new LayoutManager();
});

// Export for use in other scripts
window.LayoutManager = LayoutManager;