document.addEventListener('DOMContentLoaded', function() {
    // Show the edit form when the Modify button is clicked
    document.querySelectorAll('.modify-button').forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.dataset.courseId;
            document.getElementById(`edit-row-${courseId}`).style.display = 'table-row'; // Show the edit form
        });
    });

    document.querySelectorAll('.edit-course-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
    
            const courseId = this.dataset.courseId;
            const formData = new FormData(this);
    
            // Ensure cost is included, even if it's 0.00
            if (!formData.has('cost') || formData.get('cost') === '') {
                formData.set('cost', '0.00');
            }
    
            fetch(`/modify_course_ajax/${courseId}`, {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the course row with the new details, including cost
                    const courseRow = document.getElementById(`course-row-${courseId}`);
                    courseRow.children[0].textContent = formData.get('industry');
                    courseRow.children[1].textContent = formData.get('course_name');
                    courseRow.children[2].textContent = formData.get('course_type');
                    courseRow.children[3].textContent = formData.get('duration');
                    courseRow.children[4].textContent = formData.get('course_structure');
                    courseRow.children[5].textContent = formData.get('key_learnings');
                    courseRow.children[6].textContent = `$${parseFloat(formData.get('cost')).toFixed(2)}`;

    
                    // Hide the edit form
                    document.getElementById(`edit-row-${courseId}`).style.display = 'none';
                } else {
                    alert('Error updating course');
                }
            })
            .catch(error => console.log('Error:', error));
        });
    });
    

    // Handle Cancel button for hiding the edit form
    document.querySelectorAll('.cancel-button').forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.dataset.courseId;
            document.getElementById(`edit-row-${courseId}`).style.display = 'none'; // Hide the edit form
        });
    });

    // Handle delete course with AJAX
    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default behavior
            const courseId = this.dataset.courseId;
            const courseRow = document.getElementById(`course-row-${courseId}`);

            // Confirm the deletion
            const confirmation = confirm('Are you sure you want to delete this course?');
            if (!confirmation) {
                return;
            }

            // Temporarily hide the course row immediately
            courseRow.style.display = 'none';

            // Send the AJAX request to delete the course
            fetch(`/delete_course/${courseId}`, {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    // Show the row again if deletion failed
                    courseRow.style.display = 'table-row';
                    alert('Error deleting course.');
                }
            })
            .catch(error => {
                // Show the row again if an error occurred
                courseRow.style.display = 'table-row';
                console.error('Error deleting course:', error);
            });
        });
    });
});
