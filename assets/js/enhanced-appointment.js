document.addEventListener("DOMContentLoaded", function () {
  const appointmentForm = document.getElementById("appointmentForm");
  const calendarContainer = document.getElementById("calendarContainer");
  const timeSlotsContainer = document.getElementById("timeSlotsContainer");
  const doctorSelect = document.getElementById("doctorSelect");
  const selectedDateDisplay = document.getElementById("selectedDateDisplay");
  const selectedTimeDisplay = document.getElementById("selectedTimeDisplay");
  const selectedDoctorDisplay = document.getElementById("selectedDoctorDisplay");

  let selectedDate = null;
  let selectedTime = null;
  let selectedDoctorId = null;
  let currentMonth = new Date().getMonth();
  let currentYear = new Date().getFullYear();

  // Available time slots (can be made dynamic based on doctor availability)
  const timeSlots = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"
  ];

  // Initialize calendar
  function initCalendar() {
    renderCalendar();
    fetchDoctors();
  }

  // Render calendar
  function renderCalendar() {
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    const today = new Date();
    
    const monthNames = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ];

    let calendarHTML = `
      <div class="calendar-header">
        <button type="button" class="calendar-nav" onclick="changeMonth(-1)">‹</button>
        <h3>${monthNames[currentMonth]} ${currentYear}</h3>
        <button type="button" class="calendar-nav" onclick="changeMonth(1)">›</button>
      </div>
      <div class="calendar-grid">
        <div class="calendar-day-header">Sun</div>
        <div class="calendar-day-header">Mon</div>
        <div class="calendar-day-header">Tue</div>
        <div class="calendar-day-header">Wed</div>
        <div class="calendar-day-header">Thu</div>
        <div class="calendar-day-header">Fri</div>
        <div class="calendar-day-header">Sat</div>
    `;

    // Empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
      calendarHTML += '<div class="calendar-day empty"></div>';
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentYear, currentMonth, day);
      const isToday = date.toDateString() === today.toDateString();
      const isPast = date < today.setHours(0, 0, 0, 0);
      const isSelected = selectedDate && date.toDateString() === selectedDate.toDateString();
      
      let dayClass = "calendar-day";
      if (isToday) dayClass += " today";
      if (isPast) dayClass += " past";
      if (isSelected) dayClass += " selected";
      
      calendarHTML += `
        <div class="${dayClass}" ${!isPast ? `onclick="selectDate(${currentYear}, ${currentMonth}, ${day})"` : ''}>
          ${day}
        </div>
      `;
    }

    calendarHTML += '</div>';
    calendarContainer.innerHTML = calendarHTML;
  }

  // Change month
  window.changeMonth = function(direction) {
    currentMonth += direction;
    if (currentMonth < 0) {
      currentMonth = 11;
      currentYear--;
    } else if (currentMonth > 11) {
      currentMonth = 0;
      currentYear++;
    }
    renderCalendar();
  };

  // Select date
  window.selectDate = function(year, month, day) {
    selectedDate = new Date(year, month, day);
    selectedTime = null; // Reset time selection
    
    renderCalendar();
    renderTimeSlots();
    updateSelectedDisplay();
  };

  // Render time slots
  async function renderTimeSlots() {
    if (!selectedDate) {
      timeSlotsContainer.innerHTML = '<p class="no-selection">Please select a date first</p>';
      return;
    }

    if (!selectedDoctorId) {
      timeSlotsContainer.innerHTML = '<p class="no-selection">Please select a doctor first</p>';
      return;
    }

    try {
      // Show loading state
      timeSlotsContainer.innerHTML = '<p class="no-selection">Loading available slots...</p>';
      
      // Fetch availability for selected doctor and date
      const dateStr = selectedDate.toISOString().split('T')[0];
      const response = await fetch(`/doctor/availability/${selectedDoctorId}?date=${dateStr}`);
      const availability = await response.json();
      
      let timeSlotsHTML = '<h4>Available Time Slots</h4><div class="time-slots-grid">';
      
      timeSlots.forEach(time => {
        const isSelected = selectedTime === time;
        const isAvailable = availability.available_slots.includes(time);
        
        let slotClass = "time-slot";
        if (isSelected) slotClass += " selected";
        if (!isAvailable) slotClass += " unavailable";
        
        const clickHandler = isAvailable ? `onclick="selectTime('${time}')"` : '';
        
        timeSlotsHTML += `
          <button type="button" class="${slotClass}" ${clickHandler} ${!isAvailable ? 'disabled' : ''}>
            ${formatTime(time)}
            ${!isAvailable ? '<br><small>Booked</small>' : ''}
          </button>
        `;
      });

      timeSlotsHTML += '</div>';
      timeSlotsContainer.innerHTML = timeSlotsHTML;
    } catch (error) {
      console.error('Error fetching availability:', error);
      timeSlotsContainer.innerHTML = '<p class="no-selection">Error loading time slots</p>';
    }
  }

  // Select time
  window.selectTime = function(time) {
    selectedTime = time;
    renderTimeSlots();
    updateSelectedDisplay();
  };

  // Format time for display
  function formatTime(time) {
    const [hours, minutes] = time.split(':');
    const hour12 = hours > 12 ? hours - 12 : hours;
    const ampm = hours >= 12 ? 'PM' : 'AM';
    return `${hour12}:${minutes} ${ampm}`;
  }

  // Update selected display
  function updateSelectedDisplay() {
    if (selectedDate) {
      selectedDateDisplay.textContent = selectedDate.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } else {
      selectedDateDisplay.textContent = 'No date selected';
    }

    if (selectedTime) {
      selectedTimeDisplay.textContent = formatTime(selectedTime);
    } else {
      selectedTimeDisplay.textContent = 'No time selected';
    }

    if (selectedDoctorId) {
      const doctorOption = doctorSelect.querySelector(`option[value="${selectedDoctorId}"]`);
      selectedDoctorDisplay.textContent = doctorOption ? doctorOption.textContent : 'No doctor selected';
    } else {
      selectedDoctorDisplay.textContent = 'No doctor selected';
    }
  }

  // Fetch doctors for dropdown
  async function fetchDoctors() {
    try {
      const response = await fetch("/admin/doctors-list");
      const doctors = await response.json();
      
      doctorSelect.innerHTML = '<option value="">Select Doctor</option>';
      doctors.forEach((doctor) => {
        doctorSelect.innerHTML += `<option value="${doctor.id}">${doctor.name} (${doctor.department})</option>`;
      });
    } catch (error) {
      console.error("Error fetching doctors:", error);
    }
  }

  // Handle doctor selection
  doctorSelect.addEventListener('change', function() {
    selectedDoctorId = this.value;
    selectedTime = null; // Reset time selection when doctor changes
    updateSelectedDisplay();
    if (selectedDate && selectedDoctorId) {
      renderTimeSlots(); // Refresh time slots for new doctor
    }
  });

  // Handle form submission
  appointmentForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    if (!selectedDate || !selectedTime || !selectedDoctorId) {
      alert("Please select a date, time, and doctor for your appointment.");
      return;
    }

    const appointmentDateTime = new Date(selectedDate);
    const [hours, minutes] = selectedTime.split(':');
    appointmentDateTime.setHours(parseInt(hours), parseInt(minutes), 0);

    const formattedDateTime = appointmentDateTime.toISOString().slice(0, 19).replace('T', ' ');

    const formData = {
      patient_id: parseInt(localStorage.getItem("user_id")),
      doctor_id: parseInt(selectedDoctorId),
      appointment_time: formattedDateTime,
      status: "pending",
    };

    try {
      const response = await fetch("/admin/appointment", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        document.getElementById("bookAppointmentModal").style.display = "none";
        
        // Reset form
        selectedDate = null;
        selectedTime = null;
        selectedDoctorId = null;
        doctorSelect.value = "";
        renderCalendar();
        timeSlotsContainer.innerHTML = '<p class="no-selection">Please select a date first</p>';
        updateSelectedDisplay();
        
        // Refresh dashboard
        if (typeof loadDashboardInfo === 'function') {
          await loadDashboardInfo();
        }
        
        alert("Appointment booked successfully!");
      } else {
        const errorData = await response.json();
        alert(`Error booking appointment: ${errorData.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error booking appointment:", error);
      alert("Failed to book appointment. Please try again.");
    }
  });

  // Initialize when modal opens
  document.querySelector('[data-modal="bookAppointmentModal"]')?.addEventListener("click", () => {
    initCalendar();
  });

  // Initialize immediately if elements exist
  if (calendarContainer) {
    initCalendar();
  }
});