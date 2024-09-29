document.addEventListener('DOMContentLoaded', function() {
    // Show the edit form when the Modify button is clicked
    document.querySelectorAll('.modify-button').forEach(button => {
        button.addEventListener('click', function() {
            const courseId = this.dataset.courseId;
            document.getElementById(`edit-row-${courseId}`).style.display = 'table-row'; // Show the edit form
        });
    });

    // Handle form submission for editing courses
    document.querySelectorAll('.edit-course-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
    
            const courseId = this.dataset.courseId;
            const formData = new FormData(this);
    
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

    // Handle delete course with AJAX
    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default behavior
            const courseId = this.dataset.courseId;
            const courseRow = document.getElementById(`course-row-${courseId}`);

            const confirmation = confirm('Are you sure you want to delete this course?');
            if (!confirmation) {
                return;
            }

            courseRow.style.display = 'none';

            fetch(`/delete_course/${courseId}`, {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    courseRow.style.display = 'table-row';
                    alert('Error deleting course.');
                }
            })
            .catch(error => {
                courseRow.style.display = 'table-row';
                console.error('Error deleting course:', error);
            });
        });
    });
});
