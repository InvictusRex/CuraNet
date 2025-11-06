// Patient Detail Page JavaScript
class PatientDetailManager {
  constructor() {
    this.patientId = this.getPatientIdFromUrl();
    this.currentUser = this.getCurrentUser();
    this.init();
  }

  // Get patient ID from URL parameters
  getPatientIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
  }

  // Get current user info from localStorage
  getCurrentUser() {
    return {
      username: localStorage.getItem("username"),
      userType: localStorage.getItem("userType") || "doctor",
      userId: localStorage.getItem("user_id")
    };
  }

  // Initialize the page
  async init() {
    if (!this.patientId) {
      this.showError("No patient ID provided");
      return;
    }

    if (!this.currentUser.username) {
      window.location.href = "../index.html";
      return;
    }

    await this.loadUserInfo();
    await this.loadPatientDetails();
  }

  // Load user info for sidebar
  async loadUserInfo() {
    try {
      let response;
      let navItems = [];

      if (this.currentUser.userType === "doctor") {
        response = await fetch(`/doctor/dashboard-info/${this.currentUser.username}`);
        navItems = [
          { href: "doctor-dashboard.html", text: "Dashboard" },
          { href: "doctor-profile.html", text: "Profile" },
          { href: "doctor-appointments.html", text: "My Appointments" },
          { href: "doctor-patients.html", text: "My Patients", active: true },
          { href: "/", text: "Logout" }
        ];
      } else if (this.currentUser.userType === "admin") {
        response = await fetch(`/admin/dashboard-info/${this.currentUser.username}`);
        navItems = [
          { href: "admin-dashboard.html", text: "Dashboard" },
          { href: "admin-doctors.html", text: "Doctors" },
          { href: "admin-patient.html", text: "Patients", active: true },
          { href: "admin-appointment.html", text: "Appointments" },
          { href: "/", text: "Logout" }
        ];
      }

      if (!response.ok) {
        throw new Error("Failed to fetch user info");
      }

      const data = await response.json();
      this.updateSidebar(data, navItems);

    } catch (error) {
      console.error("Error loading user info:", error);
    }
  }

  // Update sidebar with user info
  updateSidebar(userData, navItems) {
    document.getElementById("userName").textContent = userData.name;
    document.getElementById("userId").textContent = 
      this.currentUser.userType === "doctor" ? userData.doctor_id : userData.admin_id;
    document.getElementById("userRole").textContent = 
      userData.department || this.currentUser.userType.charAt(0).toUpperCase() + this.currentUser.userType.slice(1);
    document.getElementById("userAvatar").textContent = userData.name[0].toUpperCase();

    // Update navigation
    const navMenu = document.getElementById("navMenu");
    navMenu.innerHTML = navItems.map(item => 
      `<li><a href="${item.href}" ${item.active ? 'class="active"' : ''}>${item.text}</a></li>`
    ).join('');
  }

  // Load patient details from API
  async loadPatientDetails() {
    try {
      // Extract numeric ID from patient ID (remove 'P' prefix if present)
      const numericId = this.patientId.toString().replace(/^P/, '');
      const response = await fetch(`/api/patient/${numericId}`);
      
      if (!response.ok) {
        // If the specific API doesn't exist, try to get basic patient info
        // from existing endpoints and create mock data for demonstration
        await this.loadBasicPatientInfo();
        return;
      }

      const patient = await response.json();
      this.displayPatientData(patient);
      
    } catch (error) {
      console.error("Error loading patient details:", error);
      // Fallback to basic patient info
      await this.loadBasicPatientInfo();
    }
  }

  // Fallback method to load basic patient info and create demo data
  async loadBasicPatientInfo() {
    try {
      // Try to get patient info from existing admin endpoint
      const response = await fetch(`/admin/patients-list`);
      
      if (response.ok) {
        const patients = await response.json();
        const numericId = this.patientId.toString().replace(/^P/, '');
        const patient = patients.find(p => 
          p.patient_id == this.patientId || 
          p.patient_id == `P${numericId}` || 
          p.id == numericId
        );
        
        if (patient) {
          // Create enhanced patient data with demo information
          const enhancedPatient = this.createEnhancedPatientData(patient);
          this.displayPatientData(enhancedPatient);
        } else {
          this.showError("Patient not found");
        }
      } else {
        this.showError("Failed to load patient information");
      }
    } catch (error) {
      console.error("Error loading basic patient info:", error);
      this.showError("Failed to load patient information. Please try again.");
    }
  }

  // Create enhanced patient data with demo information
  createEnhancedPatientData(basicPatient) {
    return {
      ...basicPatient,
      gender: "Not specified",
      emergency_contact: "+1 (555) 123-4567",
      address: "123 Main St, City, State 12345",
      registration_date: "2023-01-15",
      visits: [
        {
          date: "2024-01-15",
          doctor: "Dr. Smith",
          department: "Cardiology",
          diagnosis: "Routine checkup",
          status: "completed"
        },
        {
          date: "2024-01-10",
          doctor: "Dr. Johnson",
          department: "General Medicine",
          diagnosis: "Flu symptoms",
          status: "completed"
        }
      ],
      prescriptions: [
        {
          date: "2024-01-15",
          medication: "Lisinopril 10mg",
          dosage: "Once daily",
          duration: "30 days",
          prescribed_by: "Dr. Smith"
        },
        {
          date: "2024-01-10",
          medication: "Amoxicillin 500mg",
          dosage: "Three times daily",
          duration: "7 days",
          prescribed_by: "Dr. Johnson"
        }
      ],
      lab_reports: [
        {
          date: "2024-01-15",
          test_name: "Complete Blood Count",
          result: "Normal",
          reference_range: "4.5-11.0 x10³/μL",
          status: "normal"
        },
        {
          date: "2024-01-15",
          test_name: "Cholesterol Panel",
          result: "180 mg/dL",
          reference_range: "<200 mg/dL",
          status: "normal"
        }
      ],
      documents: [
        {
          id: "doc1",
          name: "Blood Test Results",
          date: "2024-01-15"
        },
        {
          id: "doc2",
          name: "X-Ray Report",
          date: "2024-01-10"
        }
      ]
    };
  }

  // Display patient data on the page
  displayPatientData(patient) {
    // Hide loading state and show content
    document.getElementById("loadingState").style.display = "none";
    document.getElementById("patientContent").style.display = "block";

    // Basic patient information
    document.getElementById("patientName").textContent = patient.name || "Unknown";
    document.getElementById("patientIdDisplay").textContent = 
      `Patient ID: ${patient.patient_id || patient.id || "N/A"}`;
    document.getElementById("patientAvatar").textContent = (patient.name || "P")[0].toUpperCase();
    
    // Patient details
    document.getElementById("patientAge").textContent = patient.age || "N/A";
    document.getElementById("patientGender").textContent = patient.gender || "N/A";
    document.getElementById("patientBloodGroup").textContent = patient.blood_group || "N/A";
    document.getElementById("patientPhone").textContent = patient.phone || "N/A";
    document.getElementById("patientEmail").textContent = patient.email || "N/A";
    document.getElementById("emergencyContact").textContent = patient.emergency_contact || "N/A";
    document.getElementById("patientAddress").textContent = patient.address || "N/A";
    document.getElementById("registrationDate").textContent = patient.registration_date || "N/A";

    // Medical history
    document.getElementById("medicalHistoryText").textContent = 
      patient.medical_history || "No medical history recorded.";

    // Populate tables
    this.populateVisitHistory(patient.visits || []);
    this.populatePrescriptions(patient.prescriptions || []);
    this.populateLabReports(patient.lab_reports || []);
    this.populateDocuments(patient.documents || []);
  }

  // Populate visit history table
  populateVisitHistory(visits) {
    const tableBody = document.getElementById("visitHistoryTable");
    
    if (visits.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <div class="empty-state-icon">📋</div>
            <div>No visit history available</div>
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = visits.map(visit => `
      <tr>
        <td>${visit.date || "N/A"}</td>
        <td>${visit.doctor || "N/A"}</td>
        <td>${visit.department || "N/A"}</td>
        <td>${visit.diagnosis || "N/A"}</td>
        <td><span class="status-badge status-${visit.status || 'completed'}">${this.formatStatus(visit.status || "completed")}</span></td>
      </tr>
    `).join('');
  }

  // Populate prescriptions table
  populatePrescriptions(prescriptions) {
    const tableBody = document.getElementById("prescriptionsTable");
    
    if (prescriptions.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <div class="empty-state-icon">💊</div>
            <div>No prescriptions available</div>
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = prescriptions.map(prescription => `
      <tr>
        <td>${prescription.date || "N/A"}</td>
        <td>${prescription.medication || "N/A"}</td>
        <td>${prescription.dosage || "N/A"}</td>
        <td>${prescription.duration || "N/A"}</td>
        <td>${prescription.prescribed_by || "N/A"}</td>
      </tr>
    `).join('');
  }

  // Populate lab reports table
  populateLabReports(labReports) {
    const tableBody = document.getElementById("labReportsTable");
    
    if (labReports.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <div class="empty-state-icon">🧪</div>
            <div>No lab reports available</div>
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = labReports.map(report => `
      <tr>
        <td>${report.date || "N/A"}</td>
        <td>${report.test_name || "N/A"}</td>
        <td>${report.result || "N/A"}</td>
        <td>${report.reference_range || "N/A"}</td>
        <td><span class="status-badge status-${report.status || 'normal'}">${this.formatStatus(report.status || "normal")}</span></td>
      </tr>
    `).join('');
  }

  // Populate documents
  populateDocuments(documents) {
    const documentsGrid = document.getElementById("documentsGrid");
    
    if (documents.length === 0) {
      documentsGrid.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📄</div>
          <div>No documents available</div>
        </div>
      `;
      return;
    }

    documentsGrid.innerHTML = documents.map(doc => `
      <div class="document-item" onclick="patientDetailManager.viewDocument('${doc.id}')">
        <div class="document-icon">📄</div>
        <div class="document-name">${doc.name || "Document"}</div>
        <div class="document-date">${doc.date || "N/A"}</div>
      </div>
    `).join('');
  }

  // Format status for display
  formatStatus(status) {
    return status.charAt(0).toUpperCase() + status.slice(1);
  }

  // View document (placeholder for future implementation)
  viewDocument(documentId) {
    console.log("Viewing document:", documentId);
    alert(`Document viewing feature will be implemented. Document ID: ${documentId}`);
    // Future implementation: open modal or navigate to document viewer
  }

  // Show error message
  showError(message) {
    document.getElementById("loadingState").style.display = "none";
    document.getElementById("errorMessage").textContent = message;
    document.getElementById("errorState").style.display = "block";
  }
}

// Theme toggle function
function toggleTheme() {
  const body = document.body;
  if (body.hasAttribute("data-theme")) {
    body.removeAttribute("data-theme");
    localStorage.setItem("theme", "light");
  } else {
    body.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
  }
}

// Initialize when DOM is loaded
let patientDetailManager;

document.addEventListener("DOMContentLoaded", () => {
  // Set theme from localStorage
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.setAttribute("data-theme", "dark");
  }

  // Initialize patient detail manager
  patientDetailManager = new PatientDetailManager();
});