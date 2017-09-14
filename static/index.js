$(function() {
  let certCount = 1
  let certs = []
  let html = `<div class="card mb-5" id="cert_{certID}">
    <div class="card-header">
      Certification {ind}
    </div>
    <img class="card-img-top" id="certImg_{certID}" src="/static/loading.gif" alt="" />
  </div>`
  $('#addCert').click(function() {
    if($('#certID').val()) {
      let cert_id = $('#certID').val()
      $('#certID').val('')
      $('#certForm').before(html.replace(/\{ind\}/g, certCount).replace(/\{certID\}/g, cert_id))
      certCount++
      $('#curCount').text(certCount)
      $.get(`/${cert_id}/fetch`, function(json) {
        console.log(json)
        if(json.success) {
          $(`#certImg_${cert_id}`).attr('src', json.data)
          $.get(`/${cert_id}/crawl`, function(json) {
            console.log(json)
            if(json.success) {
              $(`#cert_${cert_id}`).append(`<div class="card-body">
                <h4 class="card-title">${json.data.course_name}</h4>
                <div class="row">
                  <div class="col">
                    <div class="card-text">Teacher: ${json.data.teacher_name}</div>
                  </div>
                  <div class="col">
                    <div class="card-text">School: ${json.data.school_name}</div>
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <div class="card-text">Total Weeks: ${json.data.weeks}</div>
                  </div>
                  <div class="col">
                    <div class="card-text">Hours Per Week: ${json.data.min_hours_a_week}-${json.data.max_hours_a_week}</div>
                  </div>
                </div>
                <div class="card-text">Complete Date: ${json.data.complete_date}</div>
              </div>`)
              certs.push(cert_id)
              $('#makeWall').removeClass('d-none')
            } else {
              alert(json.error)
            }
          }, 'json')
        } else {
          $('#cert' + certCount).removeClass('is-valid').addClass('is-invalid')
          alert(json.error)
        }
      }, 'json')
    } else if(cert_id === '') {
      $('#certID').removeClass('is-valid').addClass('is-invalid')
      alert('Certification ID can not be empty!')
      return
    }
  })

  $('#makeWall').click(function() {
    location.href = `/wall?certs=${certs.join('&certs=')}`
  })
})
