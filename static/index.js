$(function() {
  let certCount = 1
  let html = `<div class="form-group">
    <label for="vert{ind}">Certification {ind}</label>
    <div class="input-group">
      <span class="input-group-addon" id="basic-addon{ind}">https://coursera.org/verify/</span>
      <input type="text" name="certs" class="form-control" id="cert{ind}" aria-describedby="basic-addon{ind}">
    </div>
  </div>`
  $('#addCert').click(function() {
    let cert_id = $('#cert' + certCount).val()
    $that = $(this)
    $('#loading')..modal('show')
    $.get('/verify/' + cert_id, function(json) {
      console.log(json)
      $('#loading').modal('hide')
      if(json.success) {
        $('#cert' + certCount).removeClass('is-invalid').addClass('is-valid')
        certCount++
        $that.parent().before(html.replace(/\{ind\}/g, certCount))
      } else {
        $('#cert' + certCount).removeClass('is-valid').addClass('is-invalid')
        alert(json.error)
      }
    }, 'json')
  })
  $('form').submit(function(e) {
    $('#loading').modal('show')
    if($('input[name=certs]:not(.is-valid)').length === 0) {
      return true
    } else {
      e.preventDefault()
      $('input[name=certs]:not(.is-valid)').each(function() {
        var $that = $(this)
        let cert_id = $(this).val()
        $.get('/verify/' + cert_id, function(json) {
          console.log(json)
          $('#loading').modal('hide')
          if(json.success) {
            $that.removeClass('is-invalid').addClass('is-valid')
            $('form').submit()
          } else {
            $that.removeClass('is-valid').addClass('is-invalid')
            alert(json.error)
            return false
          }
        }, 'json')
      })
    }
  })
})
