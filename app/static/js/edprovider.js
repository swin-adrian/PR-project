document.addEventListener('DOMContentLoaded', function() {
    // Show the edit form when the Modify button is clicked
    document.querySelectorAll('.modify-button').forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.dataset.courseId;
            document.getElementById(`edit-row-${courseId}`).style.display = 'table-row'; // Show the edit form
        });
    });

    // Handle form submission with AJAX
    document.querySelectorAll('.edit-course-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent form from submitting normally

            const courseId = this.dataset.courseId;
            const formData = new FormData(this);

            // Send the AJAX request
            fetch(`/modify_course_ajax/${courseId}`, {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the course row with new details
                    const courseRow = document.getElementById(`course-row-${courseId}`);
                    courseRow.children[0].textContent = formData.get('industry');
                    courseRow.children[1].textContent = formData.get('course_name');
                    courseRow.children[2].textContent = formData.get('course_type');
                    courseRow.children[3].textContent = formData.get('duration');
                    courseRow.children[4].textContent = formData.get('course_structure');
                    courseRow.children[5].textContent = formData.get('key_learnings');

                    // Hide the edit form
                    document.getElementById(`edit-row-${courseId}`).style.display = 'none';
                } else {
                    alert('Error updating course');
                }
            })
            .catch(error => console.log('Error:', error));
        });
    });

    // Handle Cancel button
    document.querySelectorAll('.cancel-button').forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.dataset.courseId;
            document.getElementById(`edit-row-${courseId}`).style.display = 'none'; // Hide the edit form
        });
    });
});