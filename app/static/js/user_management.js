document.addEventListener("DOMContentLoaded", function() {
    // Get modal elements
    var userModal = document.getElementById("userModal");
    var modifyModal = document.getElementById("modifyModal");

    // Get open modal buttons
    var openModalBtn = document.getElementById("openModalBtn");
    var closeModalBtns = document.querySelectorAll(".close");

    // Open Add User modal
    openModalBtn.addEventListener("click", function() {
        userModal.style.display = "block";
    });

    // Close modals
    closeModalBtns.forEach(function(btn) {
        btn.addEventListener("click", function() {
            userModal.style.display = "none";
            modifyModal.style.display = "none";
        });
    });

    // Close modals on outside click
    window.addEventListener("click", function(event) {
        if (event.target == userModal) {
            userModal.style.display = "none";
        }
        if (event.target == modifyModal) {
            modifyModal.style.display = "none";
        }
    });

    // Listen for modify button clicks
    document.querySelectorAll('.modify-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var userId = this.getAttribute('data-user-id');
            var userEmail = this.getAttribute('data-user-email');

            // Set the values in the modify form
            document.getElementById('modifyUserId').value = userId;
            document.getElementById('modifyEmail').value = userEmail;

            // Clear the password field
            document.getElementById('modifyPassword').value = '';

            // Open the modify modal
            modifyModal.style.display = 'block';
        });
    });

    // Handle Modify User form submission
    document.getElementById('modifyUserForm').addEventListener('submit', function(event) {
        event.preventDefault();

        var userId = document.getElementById('modifyUserId').value;
        var email = document.getElementById('modifyEmail').value;
        var password = document.getElementById('modifyPassword').value;

        // Create a form data object
        var formData = new URLSearchParams();
        formData.append('email', email);
        if (password) {
            formData.append('password', password);
        }

        // AJAX request to modify user
        fetch(`/modify_user_ajax/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        }).then(response => response.json()).then(data => {
            if (data.success) {
                // Update the table with the new email and role
                var userRow = document.getElementById(`user-row-${userId}`);
                userRow.querySelector('td:nth-child(1)').innerText = email; // Update email
                userRow.querySelector('td:nth-child(2)').innerText = data.role; // Update role

                alert('User modified successfully!');
                modifyModal.style.display = 'none';
            } else {
                alert('Failed to modify user: ' + data.message);
            }
        }).catch(error => console.error('Error:', error));
    });

    // Listen for delete button clicks
    document.querySelectorAll('.delete-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var userId = this.getAttribute('data-user-id');

            if (confirm('Are you sure you want to delete this user?')) {
                // AJAX request to delete user
                fetch(`/delete_user/${userId}`, {
                    method: 'POST'
                }).then(response => response.json()).then(data => {
                    if (data.success) {
                        alert('User deleted successfully!');
                        document.getElementById(`user-row-${userId}`).remove();
                    } else {
                        alert('Failed to delete user.');
                    }
                }).catch(error => console.error('Error:', error));
            }
        });
    });
});
