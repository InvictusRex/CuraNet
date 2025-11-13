// Patient Sidebar Component
const PatientSidebar = {
    // Standard sidebar HTML
    getHTML: (activeTab = '') => {
        return `
            <aside class="sidebar">
                <div class="user-info">
                    <div class="user-avatar" id="userAvatar">P</div>
                    <h3 id="userName">Loading...</h3>
                    <p id="patientId">Loading...</p>
                </div>

                <ul class="nav-menu">
                    <li><a href="patient-dashboard.html" ${activeTab === 'dashboard' ? 'class="active"' : ''}>Dashboard</a></li>
                    <li><a href="patient-profile.html" ${activeTab === 'profile' ? 'class="active"' : ''}>Profile</a></li>
                    <li><a href="patient-medical-history.html" ${activeTab === 'history' ? 'class="active"' : ''}>Medical History</a></li>
                    <li><a href="patient-reports.html" ${activeTab === 'reports' ? 'class="active"' : ''}>Medical Reports</a></li>
                    <li><a href="file-sharing.html" ${activeTab === 'sharing' ? 'class="active"' : ''}>File Sharing</a></li>
                    <li><a href="/" ${activeTab === 'logout' ? 'class="active"' : ''}>Logout</a></li>
                </ul>
            </aside>
        `;
    },

    // Standard CSS
    getCSS: () => {
        return `
            :root {
                --bg-primary: #0a0a0a;
                --bg-secondary: #141414;
                --text-primary: #ffffff;
                --text-secondary: #a1a1a1;
                --border-color: #2a2a2a;
                --primary-color: #2196f3;
                --success-color: #4caf50;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }

            body {
                background-color: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                transition: background-color 0.3s, color 0.3s;
            }

            .dashboard-container {
                display: flex;
                min-height: 100vh;
            }

            .sidebar {
                width: 280px;
                background-color: var(--bg-secondary);
                border-right: 1px solid var(--border-color);
                padding: 1.5rem;
                display: flex;
                flex-direction: column;
            }

            .user-info {
                text-align: center;
                padding: 1.5rem 0;
                border-bottom: 1px solid var(--border-color);
            }

            .user-avatar {
                width: 60px;
                height: 60px;
                background: var(--primary-color);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem;
                color: white;
                font-size: 1.5rem;
            }

            .user-info h3 {
                color: var(--text-primary);
                margin-bottom: 0.5rem;
            }

            .user-info p {
                color: var(--text-secondary);
            }

            .nav-menu {
                list-style: none;
                margin-top: 2rem;
            }

            .nav-menu li a {
                display: block;
                padding: 1rem;
                color: var(--text-secondary);
                text-decoration: none;
                border-radius: 8px;
                transition: all 0.2s;
            }

            .nav-menu li a:hover,
            .nav-menu li a.active {
                background: var(--bg-primary);
                color: var(--text-primary);
            }

            .main-content {
                flex: 1;
                padding: 2rem;
                overflow-y: auto;
            }

            @media (max-width: 768px) {
                .dashboard-container {
                    flex-direction: column;
                }
                .sidebar {
                    width: 100%;
                }
            }
        `;
    },

    // Initialize sidebar
    init: (activeTab = '') => {
        // Add CSS
        const style = document.createElement('style');
        style.textContent = PatientSidebar.getCSS();
        document.head.appendChild(style);

        // Load patient info
        PatientSidebar.loadPatientInfo();
    },

    // Load patient information
    loadPatientInfo: async () => {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const patientId = urlParams.get('id') || '1';
            
            const response = await fetch(`/api/patient/${patientId}`);
            if (response.ok) {
                const patient = await response.json();
                
                document.getElementById('userName').textContent = patient.name;
                document.getElementById('patientId').textContent = `ID: P${patient.id}`;
                document.getElementById('userAvatar').textContent = patient.name[0].toUpperCase();
            }
        } catch (error) {
            console.log('Could not load patient info');
        }
    }
};

// Auto-initialize if in patient page
if (window.location.pathname.includes('patient-') || window.location.pathname.includes('file-sharing')) {
    document.addEventListener('DOMContentLoaded', () => {
        PatientSidebar.init();
    });
}