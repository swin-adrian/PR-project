$(document).ready(function() {
    // When the "View Profile" button is clicked
    $('.view-profile').click(function() {
        var migrantId = $(this).data('id');

        // Make an AJAX call to fetch migrant details
        $.ajax({
            url: '/migrant/' + migrantId,
            type: 'GET',
            success: function(response) {
                // Populate the modal with migrant details
                $('#migrant-email').text(response.email);
                $('#migrant-name').text(response.first_name + " " + response.last_name);
                $('#migrant-occupation').text(response.occupation);
                $('#migrant-nationality').text(response.nationality);
                $('#migrant-country').text(response.current_country);
                $('#migrant-dob').text(response.dob);

                // Show the modal
                $('#migrantProfileModal').modal('show');
            }
        });
    });
});
