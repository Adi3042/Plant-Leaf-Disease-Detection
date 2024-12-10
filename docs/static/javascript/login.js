// Toggle between Sign In and Sign Up forms
const signInBtn = document.getElementById("sign-in-btn");
const signUpBtn = document.getElementById("sign-up-btn");
const container = document.querySelector(".container");

document.addEventListener("click", (event) => {
    if (event.target.id === "sign-up-btn") {
        container.classList.add("sign-up-mode");
    } else if (event.target.id === "sign-in-btn") {
        container.classList.remove("sign-up-mode");
    }
});


document.querySelector(".sign-up-form").addEventListener("submit", async (event) => {
    event.preventDefault(); // Prevent default form submission

    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // Client-side validation
    const { username, password, confirmpassword, mobileno, countrycode } = data;

    if (username.length < 4) {
        showAlert("Username must be at least 4 characters long.");
        return;
    }

    if (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password) || !/[^\w\s]/.test(password)) {
        showAlert("Password must be at least 8 characters long and contain 1 letter, 1 digit, and 1 symbol.");
        return;
    }

    if (password !== confirmpassword) {
        showAlert("Passwords do not match.");
        return;
    }

    // Validate mobile number length
    const validMobileLengths = { "+91": 10, "+1": 10, "+44": 11 };
    if (mobileno.length !== validMobileLengths[countrycode]) {
        showAlert(`Mobile number for ${countrycode} must be ${validMobileLengths[countrycode]} digits.`);
        return;
    }

    // Send data to the server using Fetch API
    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            showAlert(result.message, "success");
            form.reset();
        } else {
            showAlert(result.message, "error");
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error("Registration failed:", error);
        showAlert("A server error occurred. Please try again.");
    }
});

// Display alert function (can be replaced with a more sophisticated modal)
function showAlert(message, type = "error") {
    const alertBox = document.createElement('div');
    alertBox.className = `alert ${type}`;
    alertBox.innerText = message;
    document.body.appendChild(alertBox);
    setTimeout(() => alertBox.remove(), 3000);
}

// Login form submission with validation and server interaction
document.querySelector("#loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();  // Prevent the default form submission

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (username.length < 4) {
        showAlert("Username must be at least 4 characters long.");
        return;
    }

    if (password.length < 8) {
        showAlert("Password must be at least 8 characters long.");
        return;
    }

    // Send login data to the server
    try {
        const response = await fetch("/login", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            showAlert('Login successful!', "success");
            window.location.href = '/dashboard'; // Redirect to dashboard or another page
        } else {
            showAlert('Error: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('An error occurred. Please try again later.');
    }
});
