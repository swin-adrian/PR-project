document.addEventListener('DOMContentLoaded', function() {
    // Show the edit form when the Modify button is clicked
    document.querySelectorAll('.modify-button').forEach(button => {
        button.addEventListener('click', function() {
            const registrationId = this.dataset.registrationId;
            document.getElementById(`edit-row-${registrationId}`).style.display = 'table-row'; // Show the edit form
        });
    });

    // Handle form submission for editing a registration
    document.querySelectorAll('.edit-registration-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
    
            const registrationId = this.dataset.registrationId;
            const formData = new FormData(this);
    
            fetch(`/modify_registration_ajax/${registrationId}`, {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the registration row with new details
                    const registrationRow = document.getElementById(`registration-row-${registrationId}`);
                    registrationRow.children[0].textContent = formData.get('course_name');
                    registrationRow.children[1].textContent = formData.get('first_name');
                    registrationRow.children[2].textContent = formData.get('last_name');
                    registrationRow.children[3].textContent = formData.get('email');
                    registrationRow.children[4].textContent = `$${parseFloat(formData.get('cost')).toFixed(2)}`;
                    registrationRow.children[5].textContent = formData.get('key_learnings');

                    document.getElementById(`edit-row-${registrationId}`).style.display = 'none'; // Hide the edit form
                } else {
                    alert('Error updating registration');
                }
            })
            .catch(error => console.log('Error:', error));
        });
    });

    // Handle delete registration with AJAX
    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default behavior
            const registrationId = this.dataset.registrationId;
            const registrationRow = document.getElementById(`registration-row-${registrationId}`);

            const confirmation = confirm('Are you sure you want to delete this registration?');
            if (!confirmation) {
                return;
            }

            // Temporarily hide the registration row
            registrationRow.style.display = 'none';

            fetch(`/delete_registration/${registrationId}`, {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    registrationRow.style.display = 'table-row'; // Show row again if deletion failed
                    alert('Error deleting registration.');
                }
            })
            .catch(error => {
                registrationRow.style.display = 'table-row'; // Show row again if an error occurred
                console.error('Error deleting registration:', error);
            });
        });
    });
});
