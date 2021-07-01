document.getElementById("pronouns").style.display = "none";

function hideField() {
    g_ind = document.getElementById("gender").selectedIndex;
    prn = document.getElementById("pronouns");
    if (g_ind === 3 || g_ind === 4) {
       prn.style.display = "block";
    }
    else{
        prn.style.display = "none";
    }
}