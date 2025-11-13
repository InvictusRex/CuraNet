// File Sharing JavaScript Module
const fileSharing = {
    // Upload file to server
    async uploadFile(file, patientId, doctorId, sessionId = null, sharedWith = []) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('patient_id', patientId);
        formData.append('doctor_id', doctorId);
        if (sessionId) formData.append('session_id', sessionId);
        formData.append('shared_with', JSON.stringify(sharedWith));

        try {
            const response = await fetch('/reports/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    },

    // Get patient reports
    async getPatientReports(patientId, doctorId) {
        try {
            const response = await fetch(`/reports/patient/${patientId}?doctor_id=${doctorId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch reports: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Fetch reports error:', error);
            throw error;
        }
    },

    // Download report
    async downloadReport(reportId, doctorId) {
        try {
            const response = await fetch(`/reports/${reportId}/download?doctor_id=${doctorId}`);
            
            if (!response.ok) {
                throw new Error(`Download failed: ${response.statusText}`);
            }

            const result = await response.json();
            
            // Open download URL in new tab
            window.open(result.download_url, '_blank');
            
            return result;
        } catch (error) {
            console.error('Download error:', error);
            throw error;
        }
    },

    // Create upload UI
    createUploadUI(containerId, patientId, doctorId) {
        const container = document.getElementById(containerId);
        
        container.innerHTML = `
            <div class="upload-section">
                <h3>Upload Medical Report</h3>
                <div class="upload-area" id="uploadArea">
                    <div class="upload-content">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7,10 12,15 17,10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                        <p>Drag and drop files here or <span class="upload-link">browse</span></p>
                        <p class="upload-hint">Supports PDF, DOC, DOCX, JPG, PNG (Max 10MB)</p>
                    </div>
                    <input type="file" id="fileInput" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" style="display: none;">
                </div>
                <div class="upload-progress" id="uploadProgress" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p id="progressText">Uploading...</p>
                </div>
                <div class="upload-result" id="uploadResult"></div>
            </div>
        `;

        // Add event listeners
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadLink = container.querySelector('.upload-link');

        // Click to browse
        uploadLink.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0], patientId, doctorId);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0], patientId, doctorId);
            }
        });
    },

    // Handle file upload
    async handleFileUpload(file, patientId, doctorId) {
        const progressDiv = document.getElementById('uploadProgress');
        const resultDiv = document.getElementById('uploadResult');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        // Show progress
        progressDiv.style.display = 'block';
        resultDiv.innerHTML = '';

        try {
            // Simulate progress (in real implementation, use XMLHttpRequest for progress tracking)
            progressFill.style.width = '30%';
            progressText.textContent = 'Uploading to server...';

            const result = await this.uploadFile(file, patientId, doctorId);

            progressFill.style.width = '100%';
            progressText.textContent = 'Upload complete!';

            setTimeout(() => {
                progressDiv.style.display = 'none';
                resultDiv.innerHTML = `
                    <div class="success-message">
                        ✅ File "${file.name}" uploaded successfully!
                    </div>
                `;
                
                // Refresh reports list
                this.refreshReportsList(patientId, doctorId);
            }, 1000);

        } catch (error) {
            progressDiv.style.display = 'none';
            resultDiv.innerHTML = `
                <div class="error-message">
                    ❌ Upload failed: ${error.message}
                </div>
            `;
        }
    },

    // Create reports list UI
    createReportsListUI(containerId, patientId, doctorId) {
        const container = document.getElementById(containerId);
        
        container.innerHTML = `
            <div class="reports-section">
                <h3>Medical Reports</h3>
                <div class="reports-list" id="reportsList">
                    <div class="loading">Loading reports...</div>
                </div>
            </div>
        `;

        this.loadReports(patientId, doctorId);
    },

    // Load and display reports
    async loadReports(patientId, doctorId) {
        const reportsList = document.getElementById('reportsList');
        
        try {
            const reports = await this.getPatientReports(patientId, doctorId);
            
            if (reports.length === 0) {
                reportsList.innerHTML = '<div class="no-reports">No reports found</div>';
                return;
            }

            reportsList.innerHTML = reports.map(report => `
                <div class="report-item">
                    <div class="report-info">
                        <h4>${report.report_name}</h4>
                        <p>Uploaded by: ${report.uploaded_by}</p>
                        <p>Date: ${new Date(report.uploaded_at).toLocaleDateString()}</p>
                        <p>Size: ${this.formatFileSize(report.file_size)}</p>
                    </div>
                    <div class="report-actions">
                        <button class="btn-download" onclick="fileSharing.downloadReport(${report.report_id}, ${doctorId})">
                            Download
                        </button>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            reportsList.innerHTML = `<div class="error-message">Failed to load reports: ${error.message}</div>`;
        }
    },

    // Refresh reports list
    refreshReportsList(patientId, doctorId) {
        this.loadReports(patientId, doctorId);
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

// CSS Styles (add to your CSS file)
const styles = `
.upload-section, .reports-section {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
}

.upload-area {
    border: 2px dashed var(--border-color);
    border-radius: 8px;
    padding: 3rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.upload-area:hover, .upload-area.drag-over {
    border-color: var(--primary-color);
    background: var(--bg-secondary);
}

.upload-content svg {
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

.upload-link {
    color: var(--primary-color);
    text-decoration: underline;
    cursor: pointer;
}

.upload-hint {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: var(--bg-secondary);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.progress-fill {
    height: 100%;
    background: var(--primary-color);
    transition: width 0.3s ease;
}

.report-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    margin-bottom: 1rem;
}

.report-info h4 {
    margin: 0 0 0.5rem 0;
    color: var(--text-primary);
}

.report-info p {
    margin: 0.25rem 0;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.btn-download {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s ease;
}

.btn-download:hover {
    background: #2563eb;
}

.success-message {
    color: var(--success-color);
    padding: 1rem;
    background: #f0fdf4;
    border-radius: 6px;
    margin-top: 1rem;
}

.error-message {
    color: var(--danger-color);
    padding: 1rem;
    background: #fef2f2;
    border-radius: 6px;
    margin-top: 1rem;
}

.loading, .no-reports {
    text-align: center;
    color: var(--text-secondary);
    padding: 2rem;
}
`;

// Add styles to document
if (!document.getElementById('file-sharing-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'file-sharing-styles';
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
}