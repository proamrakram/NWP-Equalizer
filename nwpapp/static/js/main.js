"use strict";

function valid_date(in_date) {
    //function returns error message as 'error:msg' if erroneous date supplied, or
    //message 'ok:dd-mm-yyyy' if date is ok
    // arg :  string in_date
    let err_msg = "error: not valid date";
    let lst_str = in_date.split("/");
    if (lst_str.length != 3) {
        lst_str = in_date.split("-");
    }

    if (lst_str.length != 3) {
        lst_str = in_date.split(".");
    }

    if (lst_str.length != 3) {
        return err_msg + ", components";
    }

    if (isNaN(lst_str[0]) || isNaN(lst_str[1]) || isNaN(lst_str[2])) {
        return err_msg + ", not numeric";
    }

    if (lst_str[0] > 31 || lst_str[1] > 12 || lst_str[2] < 2019) {
        return err_msg + ", values";
    }

    let in_d = new Date(lst_str[2], lst_str[1], lst_str[0]);
    // check if day is compatible with month (eg not 30/feb)

    alert("date: ");

    if (in_d.getMonth() == Number(lst_str[1])) {
        return err_msg + ", incompatible";
    }

    return "ok:" + in_d.getDate() + "-" + in_d.getMonth() + "-" + in_d.getFullYear()
}


function date_compare(hi_date,lo_date) {
    //function compares hi_date and lo_date. 
    //returns false if lo_date > hi_date
    
    let hi_str = hi_date.split("-");
    let lo_str = lo_date.split("-");
    let hi_d = new Date(hi_str[2], hi_str[1], hi_str[0]);
    let lo_d = new Date(lo_str[2], lo_str[1], lo_str[0]);
    // check if day is compatible with month (eg not 30/feb)

    alert(hi_d);
    alert(lo_d);

    return (lo_date <= hi_date);

}


function valid_date_range(in_date) {
//if in_date is within date range, ok, else error
//arg date in_date

    let d_max = new Date();
    let d_min = new Date();
    d_min.setDate(d_min.getDate()-3);
    if (in_date > d_max || in_date < d_min) {
        return "error";
    }
    return "ok";
}
