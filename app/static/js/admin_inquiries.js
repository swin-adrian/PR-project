// admin_inquiries.js

$(document).ready(function() {
    // CSRF token setup (if your application uses CSRF protection)
    var csrfToken = $('meta[name="csrf-token"]').attr('content');
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrfToken
        }
    });

    // When the Edit button is clicked
    $('.modify-btn').on('click', function() {
        // Retrieve data attributes from the clicked button
        var inquiryId = $(this).data('inquiry-id');
        var status = $(this).data('status');
        var url = $(this).data('url');

        // Log values for debugging
        console.log('Edit button clicked for inquiry ID:', inquiryId);
        console.log('Current status:', status);
        console.log('URL:', url);

        // Set values in the modal
        $('#modal-inquiry-id').val(inquiryId);
        $('#edit-inquiry-form').data('url', url);
        $('#modal-status').val(status);
    });

    // Handle form submission inside the modal
    $('#edit-inquiry-form').on('submit', function(e) {
        e.preventDefault();

        var inquiryId = $('#modal-inquiry-id').val();
        var status = $('#modal-status').val();
        var url = $(this).data('url');

        // Log values for debugging
        console.log('Submitting form for inquiry ID:', inquiryId);
        console.log('New status:', status);
        console.log('URL:', url);

        // Perform AJAX request to update the status
        $.ajax({
            url: url,
            type: 'POST',
            data: { status: status },
            success: function(response) {
                console.log('Server response:', response);
                if (response.success) {
                    // Update the status in the table
                    $('#inquiry-row-' + inquiryId + ' .status-column').text(status);
                    // Update the data-status attribute of the Edit button
                    $('.modify-btn[data-inquiry-id="' + inquiryId + '"]').data('status', status);
                    // Hide the modal
                    var modalElement = document.getElementById('editInquiryModal');
                    var modal = bootstrap.Modal.getInstance(modalElement);
                    modal.hide();
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', xhr.responseText);
                alert('Error updating inquiry: ' + xhr.responseText);
            }
        });
    });

    // Delete button logic
    $('.delete-btn').on('click', function() {
        var inquiryId = $(this).data('inquiry-id');
        var url = $(this).data('url');

        // Log values for debugging
        console.log('Delete button clicked for inquiry ID:', inquiryId);
        console.log('URL:', url);

        if (confirm('Are you sure you want to delete this inquiry?')) {
            $.ajax({
                url: url,
                type: 'POST',
                success: function(response) {
                    console.log('Server response:', response);
                    if (response.success) {
                        // Remove the inquiry row from the table
                        $('#inquiry-row-' + inquiryId).remove();
                    } else {
                        alert('Error: ' + response.message);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX error:', xhr.responseText);
                    alert('Error deleting inquiry: ' + xhr.responseText);
                }
            });
        }
    });
});
