$("#start_date").on(function() {
    $("#end_date").val($("#start_date").val());
});
$("#end_date").on(function() {
    $("#start_date").val($("#end_date").val());
});
