
    $(document).ready(function() {
        // Cache modal elements
        var registerModal = $('#registerModal');
        var registerForm = $('#registerForm');
        var selectedCourseData = null;
    
        // Initially hide the modal when the page loads
        registerModal.hide();
    
        // Close button functionality
        $(document).on('click', '.close-button', function() {
            registerModal.hide();
        });
    
        // Close modal when clicking outside of it
        $(window).click(function(event) {
            if ($(event.target).is('.modal')) {
                registerModal.hide();
            }
        });
    
        // Handle "Register" button click inside the course card
        $(document).on('click', '.register-button', function(event) {
            event.stopPropagation(); // Prevent event bubbling to parent elements
    
            var courseCard = $(this).closest('.course-card');
    
            selectedCourseData = {
                CourseID: courseCard.data('course-id'),
                CourseName: courseCard.data('course-name'),
                Industry: courseCard.data('industry'),
                CourseType: courseCard.data('course-type'),
                Duration: courseCard.data('duration'),
                Similarity_Score: courseCard.data('similarity-score'),
                Total_Points: courseCard.data('total-points')
            };
    
            // Populate the registration modal with course data
            $('#modalCourseTitle').html(`
                <strong>${selectedCourseData.CourseName}</strong>
                <p>Industry: ${selectedCourseData.Industry}</p>
                <p>Course Type: ${selectedCourseData.CourseType}</p>
                <p>Duration: ${selectedCourseData.Duration}</p>
            `);
    
            // Show the registration modal
            registerModal.show();
    
            // Set focus to the first input field
            $('#firstName').focus();
        });
    
        // Handle registration form submission
        registerForm.submit(function(event) {
            event.preventDefault(); // Prevent default form submission
    
            var formData = $(this).serializeArray(); // Get form data
    
            // Convert form data to an object
            var userData = {};
            $.each(formData, function(_, field) {
                userData[field.name] = field.value;
            });
    
            // Prepare data to send to the server
            var dataToSend = {
                courseId: selectedCourseData.CourseID,
                courseName: selectedCourseData.CourseName,
                firstName: userData.firstName,
                lastName: userData.lastName,
                email: userData.email
            };
    
            // Send data to the server via AJAX
            $.ajax({
                type: 'POST',
                url: "{{ url_for('migrant.register_course') }}",
                data: dataToSend,
                success: function(response) {
                    alert('Successfully registered for the course!');
                    
                    // Hide the modal
                    registerModal.hide();
    
                    // Reset the form
                    registerForm[0].reset();
    
                    // Remove the corresponding course card
                    $(`div[data-course-id='${selectedCourseData.CourseID}']`).remove();
                },
                error: function(error) {
                    alert('Error registering for the course. Please try again.');
                }
            });
        });
    
        // Fetch and display courses
        $.ajax({
            type: 'GET',
            url: "{{ url_for('migrant.recommendcourse') }}",
            success: function(response) {
                var courseResults = $('#courseResults');
                courseResults.empty();
    
                if (response.courses.length > 0) {
                    $.each(response.courses, function(index, course) {
                        if (course.Similarity_Score > 20) {
                            var card = `
                                <div class="course-card"
                                     data-course-id="${course.CourseID}"
                                     data-course-name="${course.CourseName}"
                                     data-industry="${course.Industry}"
                                     data-course-type="${course.CourseType}"
                                     data-duration="${course.Duration}"
                                     data-similarity-score="${course.Similarity_Score}"
                                     data-total-points="${course.Total_Points}">
                                    <div class="course-title">${course.CourseName}</div>
                                    <div class="course-info">Industry: ${course.Industry}</div>
                                    <div class="course-info">Course Type: ${course.CourseType}</div>
                                    <div class="course-info">Duration: ${course.Duration}</div>
                                    <div class="course-info">Similarity Score: ${course.Similarity_Score}%</div>
                                    <div class="course-points">Total Points: ${course.Total_Points}</div>
                                    <button class="register-button">Register</button>
                                </div>`;
                            courseResults.append(card);
                        }
                    });
    
                    if (courseResults.children().length === 0) {
                        courseResults.html('<p class="no-results">No courses found with a similarity score above 20%.</p>');
                    }
                } else {
                    courseResults.html('<p class="no-results">No courses found matching your profile.</p>');
                }
            },
            error: function(error) {
                $('#courseResults').html('<p class="no-results">Error fetching recommendations. Please try again later.</p>');
            }
        });
    });
    
    