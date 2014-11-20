function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}
    
function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function set_color_bar(min,max,palette) {
    var hex_color_list = palette.split(','),
    cb  = document.getElementById('colorbar'),
    ctx = cb.getContext('2d'),
    cb_width = parseInt(cb.width),
    cb_height = parseInt(cb.height),
    x_step = Math.floor(cb_width / hex_color_list.length);
    for(var i = 0; i < hex_color_list.length; i++) {
        rgb = hexToRgb('#' + hex_color_list[i]);
        ctx.beginPath();
        var color = 'rgb(' + rgb.r + ', ' + rgb.g + ', ' + rgb.b + ')',
        grd = ctx.createLinearGradient(i*x_step,0,(i+1)*x_step,0); //Gradient
        grd.addColorStop(0,'#' + hex_color_list[i]);
        try {
            grd.addColorStop(1,'#' + hex_color_list[i+1]);
        }
        catch(e){
            grd.addColorStop(1,'#' + hex_color_list[i]);
        }
        //ctx.fillStyle = color;
        ctx.fillStyle = grd;
        ctx.fillRect(i * x_step, 0, x_step, cb_height);
        //Text adding does not work for me, interediate solution: click function
        /* 
        ctx.font="14px Verdana black";
        var data_diff = Math.abs(parseFloat(max) - parseFloat(min)),
        data_step = Math.floor(data_diff /  (hex_color_list + 1)),
        tick = String(Math.floor(min + i*data_step));
        ctx.fillText(tick,i*x_step,cb_height);
        */
    }
    cb.onclick = function(e) {
        var x = e.offsetX;
        var data_val =  parseFloat(min) + Math.abs(parseFloat(max) - parseFloat(min)) * x /(cb_width);
        alert(data_val);
    };
}

