form_utils = {
    adjust_date: function(date_id,new_date) {
        /*
        Matches start/end dates to avoide calendar errors
        Adjust the value of the element with ID date_id 
        to new_date + 1 (tomorrow)
        */
        //Find tomorrow, need at least one day to generate map
        var yr = parseInt(new_date.substring(0,4));
        var mon = parseInt(new_date.substring(5,7)) - 1;
        var day = parseInt(new_date.substring(8,10))
        var d = new Date(yr,mon,day);
        d.setDate(d.getDate() + 1);
        yr = d.getFullYear();
        mon = ("0" + (d.getMonth() + 1)).slice(-2);
        day = ("0" + d.getDate()).slice(-2);
        document.getElementById(date_id).value = yr + '-' + mon + '-' + day;
    }
}
