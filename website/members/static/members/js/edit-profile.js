document.getElementById("id_profile_picture").addEventListener("change", function () {
    if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const image = document.getElementById("profile_image")
            image.src = e.target.result;
            const cropper = new Cropper(image, {
                viewMode: 1,
                aspectRatio: 16 / 9,
                minCropBoxWidth: 200,
                minCropBoxHeight: 200,
                crop: function (event) {
                    document.getElementById("id_x").value = event.detail.x;
                    document.getElementById("id_y").value = event.detail.y;
                    document.getElementById("id_width").value = event.detail.width;
                    document.getElementById("id_height").value = event.detail.height;
                }
            });
        }
        reader.readAsDataURL(this.files[0]);
    }
});