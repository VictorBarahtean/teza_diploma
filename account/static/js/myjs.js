function uploadPhoto(event) {
    event.preventDefault(); 
  
    var fileInput = document.getElementById('change_photo');
    
    var file = fileInput.files[0];
    if (file) {
      var reader = new FileReader();
  
      reader.onload = function(e) {
        var templateImage = document.getElementById('changed_photo');
        templateImage.src = e.target.result; 
        templateImage.classList.add('show');
      };
  
      reader.readAsDataURL(file);
    }
    else{
        templateContainer.classList.remove('show');
    }
  }

function clearPhoto(event) {
    event.preventDefault(); 
  
    var photo_changed = document.getElementById('changed_photo');
    photo_changed.classList.remove('show');
    var fileInput_value = document.getElementById('change_photo');
    var photo_current = document.getElementById('current_photo');
    fileInput_value.value = '';
    console.log(photo_current);
}