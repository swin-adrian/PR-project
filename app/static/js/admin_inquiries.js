$(document).ready(function() {
    // Show the edit form when the Edit button is clicked
    $('.edit-button').on('click', function() {
        const inquiryId = $(this).data('inquiry-id');
        $(`#edit-row-${inquiryId}`).toggle(); // Toggle the visibility of the edit form
    });

    // Handle form submission for editing an inquiry
    $('.edit-inquiry-form').on('submit', function(e) {
        e.preventDefault(); // Prevent the default form submission

        const inquiryId = $(this).data('inquiry-id');
        const status = $(this).find('select[name="status"]').val();

        $.ajax({
            type: 'POST',
            url: `/admin/modify_inquiry/${inquiryId}`, // Include '/admin' prefix
            data: { status: status },
            success: function(response) {
                if (response.success) {
                    $(`#inquiry-row-${inquiryId} .status-column`).text(status); // Update the status column
                    $(`#edit-row-${inquiryId}`).hide(); // Hide the edit form
                } else {
                    alert(response.message);
                }
            },
            error: function(error) {
                console.error('Error updating inquiry:', error);
            }
        });
    });

    // Handle delete inquiry
    $('.delete-button').on('click', function(e) {
        e.preventDefault();

        const inquiryId = $(this).data('inquiry-id');
        const confirmation = confirm('Are you sure you want to delete this inquiry?');
        if (!confirmation) return;

        $.ajax({
            type: 'POST',
            url: `/admin/delete_inquiry/${inquiryId}`, // Include '/admin' prefix
            success: function(response) {
                if (response.success) {
                    $(`#inquiry-row-${inquiryId}`).remove(); // Remove the inquiry row
                    $(`#edit-row-${inquiryId}`).remove(); // Remove the edit form row
                } else {
                    alert('Error deleting inquiry.');
                }
            },
            error: function(error) {
                console.error('Error deleting inquiry:', error);
            }
        });
    });
});
