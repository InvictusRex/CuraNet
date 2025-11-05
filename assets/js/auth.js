document.addEventListener("DOMContentLoaded", function () {
  // Role selection handling
  const roleButtons = document.querySelectorAll(".role-btn");
  const loginForm = document.getElementById("loginForm");
  let selectedRole = "patient";

  roleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      roleButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      selectedRole = button.dataset.role;
    });
  });

  // Login form submission
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Simple validation
    if (!username || !password) {
      alert("Please fill in all fields");
      return;
    }

    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          identifier: username,
          password: password,
          user_type: selectedRole
        })
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        localStorage.setItem('username', data.user.name);
        localStorage.setItem('userEmail', data.user.email);
        localStorage.setItem('userId', data.user.id);
        localStorage.setItem('userType', data.user.type);
        
        switch (selectedRole) {
          case "admin":
            window.location.href = "admin-dashboard.html";
            break;
          case "doctor":
            window.location.href = "doctor-dashboard.html";
            break;
          case "patient":
            window.location.href = "patient-dashboard.html";
            break;
        }
      } else {
        alert(data.detail || 'Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert("Login failed. Please try again.");
    }
  });
});
