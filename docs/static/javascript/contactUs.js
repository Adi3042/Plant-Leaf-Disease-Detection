// Function to validate the contact form before submission
function validateForm() {
    // Get values from input fields
    var name = document.getElementById('name').value;
    var phone = document.getElementById('phone').value;
    var email = document.getElementById('email').value;
    var message = document.getElementById('message').value;

    // Check if name is empty
    if (name.trim() == '') {
        alert('Please enter your name');
        return false;
    }

    // Check if phone number is empty
    if (phone.trim() == '') {
        alert('Please enter your phone number');
        return false;
    }

    // Check if email is empty
    if (email.trim() == '') {
        alert('Please enter your email');
        return false;
    }

    // Check if message is empty
    if (message.trim() == '') {
        alert('Please enter your message');
        return false;
    }

    // All fields are filled, return true for form submission
    return true;
}
