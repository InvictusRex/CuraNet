// Script to update all dashboard pages with unified layout
// This is a helper script to ensure consistency across all pages

const fs = require('fs');
const path = require('path');

const pagesDir = './pages';
const dashboardPages = [
  'admin-dashboard.html',
  'admin-appointment.html',
  'admin-doctors.html',
  'admin-patient.html',
  'doctor-appointments.html',
  'doctor-patients.html',
  'doctor-profile.html',
  'doctor-active-sessions.html',
  'doctor-session-management.html',
  'patient-profile.html',
  'patient-medical-history.html',
  'patient-reports.html',
  'file-sharing.html'
];

// Common navigation menus
const doctorNavigation = `
          <li><a href="doctor-dashboard.html"><span class="nav-icon">📊</span>Dashboard</a></li>
          <li><a href="doctor-profile.html"><span class="nav-icon">👤</span>Profile</a></li>
          <li><a href="doctor-appointments.html"><span class="nav-icon">📅</span>My Appointments</a></li>
          <li><a href="doctor-patients.html"><span class="nav-icon">👥</span>My Patients</a></li>
          <li><a href="doctor-active-sessions.html"><span class="nav-icon">🔄</span>Active Sessions</a></li>
          <li><a href="/"><span class="nav-icon">🚪</span>Logout</a></li>
`;

const patientNavigation = `
          <li><a href="patient-dashboard.html"><span class="nav-icon">📊</span>Dashboard</a></li>
          <li><a href="patient-profile.html"><span class="nav-icon">👤</span>Profile</a></li>
          <li><a href="patient-medical-history.html"><span class="nav-icon">📜</span>Medical History</a></li>
          <li><a href="patient-reports.html"><span class="nav-icon">📄</span>Medical Reports</a></li>
          <li><a href="file-sharing.html"><span class="nav-icon">📁</span>File Sharing</a></li>
          <li><a href="/"><span class="nav-icon">🚪</span>Logout</a></li>
`;

const adminNavigation = `
          <li><a href="admin-dashboard.html"><span class="nav-icon">📊</span>Dashboard</a></li>
          <li><a href="admin-patient.html"><span class="nav-icon">👥</span>Patients</a></li>
          <li><a href="admin-doctors.html"><span class="nav-icon">👨‍⚕️</span>Doctors</a></li>
          <li><a href="admin-appointment.html"><span class="nav-icon">📅</span>Appointments</a></li>
          <li><a href="/"><span class="nav-icon">🚪</span>Logout</a></li>
`;

function updatePage(filename) {
  const filePath = path.join(pagesDir, filename);
  
  if (!fs.existsSync(filePath)) {
    console.log(`File not found: ${filename}`);
    return;
  }

  let content = fs.readFileSync(filePath, 'utf8');
  
  // Determine page type and navigation
  let navigation = '';
  let userIdField = 'userId';
  
  if (filename.startsWith('doctor-')) {
    navigation = doctorNavigation;
    userIdField = 'doctorId';
  } else if (filename.startsWith('patient-')) {
    navigation = patientNavigation;
    userIdField = 'patientId';
  } else if (filename.startsWith('admin-')) {
    navigation = adminNavigation;
    userIdField = 'adminId';
  }

  // Update CSS imports
  if (!content.includes('global.css') && !content.includes('layout.css')) {
    content = content.replace(
      /<title>.*?<\/title>/,
      `$&
    <link rel="stylesheet" href="../assets/css/global.css">
    <link rel="stylesheet" href="../assets/css/layout.css">`
    );
  }

  // Add theme toggle and sidebar elements if not present
  if (!content.includes('sidebar-toggle')) {
    const themeTogglePattern = /<button[^>]*class="theme-toggle"[^>]*>[\s\S]*?<\/button>/;
    const themeToggleReplacement = `<!-- Theme Toggle -->
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">
      <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z"/>
      </svg>
    </button>

    <!-- Sidebar Toggle for Mobile -->
    <button class="sidebar-toggle" aria-label="Toggle sidebar">☰</button>

    <!-- Sidebar Overlay for Mobile -->
    <div class="sidebar-overlay"></div>`;

    if (themeTogglePattern.test(content)) {
      content = content.replace(themeTogglePattern, themeToggleReplacement);
    } else {
      content = content.replace(/<body[^>]*>/, `$&
    ${themeToggleReplacement}`);
    }
  }

  // Update sidebar structure
  if (content.includes('<aside class="sidebar">')) {
    const sidebarPattern = /<aside class="sidebar">[\s\S]*?<\/aside>/;
    const sidebarReplacement = `<aside class="sidebar">
        <div class="sidebar-header">
          <a href="/" class="sidebar-brand">CuraNet HMS</a>
          <button class="sidebar-close" aria-label="Close sidebar">×</button>
        </div>

        <div class="user-info">
          <div class="user-avatar" id="userAvatar">
            <!-- Will be filled by JS -->
          </div>
          <h3 id="userName">Loading...</h3>
          <p id="${userIdField}">Loading...</p>
        </div>

        <ul class="nav-menu">${navigation}
        </ul>
      </aside>`;

    content = content.replace(sidebarPattern, sidebarReplacement);
  }

  // Wrap main content in page-content div
  if (!content.includes('page-content')) {
    content = content.replace(
      /<main class="main-content">\s*(<div class="dashboard-header">)/,
      `<main class="main-content">
        <div class="page-content">
          $1`
    );
    
    content = content.replace(
      /(<\/main>)/,
      `        </div>
      $1`
    );
  }

  // Add core scripts if not present
  if (!content.includes('layout.js')) {
    content = content.replace(
      /<script src="\.\.\/assets\/js\/common\.js"><\/script>/,
      `<!-- Core Scripts -->
    <script src="../assets/js/common.js"></script>
    <script src="../assets/js/layout.js"></script>`
    );
  }

  // Set active navigation item
  const currentPageName = filename.replace('.html', '');
  content = content.replace(
    new RegExp(`<a href="${filename}"([^>]*)>`, 'g'),
    `<a href="${filename}"$1 class="active">`
  );

  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`Updated: ${filename}`);
}

// Update all dashboard pages
dashboardPages.forEach(updatePage);

console.log('All dashboard pages updated with unified layout!');