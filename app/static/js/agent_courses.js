$(document).ready(function() {
    // Fetch courses and display them
    $.get('/get_courses', function(courses) {
        let courseList = $('#course-list');
        
        // Template literal for each course card
        courses.forEach(course => {
            let courseCard = `
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">${course.CourseName}</h5>
                            <p class="card-text"><strong>Industry:</strong> ${course.Industry}</p>
                            <p class="card-text"><strong>Type:</strong> ${course.CourseType}</p>
                            <p class="card-text"><strong>Duration:</strong> ${course.Duration}</p>
                            <p class="card-text"><strong>University:</strong> ${course.University}</p> <!-- Added University field -->
                            <p class="card-text"><strong>Cost:</strong> $${course.Cost}</p>
                            <button class="btn btn-info recommend-btn" data-id="${course._id}">Recommend</button>
                        </div>
                    </div>
                </div>`;
            courseList.append(courseCard);
        });
    });
    
    // Fetch migrants when the "Recommend" button is clicked
    $(document).on('click', '.recommend-btn', function() {
        let courseId = $(this).data('id');
        $('#courseId').val(courseId);
        $.get('/linked_migrants', function(migrants) {
            let migrantSelect = $('#migrantSelect');
            migrantSelect.empty();

            // Add each migrant as an option in the dropdown
            migrants.forEach(migrant => {
                migrantSelect.append(new Option(migrant.first_name + " " + migrant.last_name, migrant._id));
            });
        });
        $('#recommendModal').modal('show');
    });

    // Handle recommendation form submission
    $('#recommendForm').submit(function(event) {
        event.preventDefault();

        // Collect data for the recommendation in an object
        let recommendationData = {
            course_id: $('#courseId').val(),
            migrant_id: $('#migrantSelect').val(),
            feedback: $('#feedback').val()
        };
        $.ajax({
            url: '/recommend_course',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(recommendationData),
            success: function() {
                alert('Recommendation submitted successfully');
                $('#recommendModal').modal('hide');
            },
            error: function() {
                alert('Failed to submit recommendation');
            }
        });
    });
});
