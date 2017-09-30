$(function() {
  let certCount = 1
  let certs = []
  let type = 'coursera'
  let html = `<div class="card mb-5" id="cert_{certID}">
    <div class="card-header">
      Certification {ind}
    </div>
    <div class="card-body bg-gray text-center">
      <img class="my-5 cert-loading" id="certImg_{certID}" src="/static/loading.svg" alt="" />
      <h3 class="my-5 text-white">Loading...</h3>
    </div>
  </div>`
  $('#addCert').click(function() {
    let cert_id = $('#certID').val()
    if(cert_id.length === 12) {
      $('#certID').val('')
      $('#certForm').before(html.replace(/\{ind\}/g, certCount).replace(/\{certID\}/g, cert_id))
      certCount++
      $('#curCount').text(certCount)
      $.get(`${type}/${cert_id}/fetch`, function(json) {
        console.log(json)
        if(json.success) {
          $(`#cert_${cert_id} .card-body`).remove()
          $(`#cert_${cert_id}`).append(`<img class="card-img-top" src="static/certs/${cert_id}.png" alt="" />`)
          let pdf_url
          if(type === 'coursera') {
            pdf_url = `https://coursera.org/verify/${cert_id}`
          } else {
            pdf_url = 'https://coursera.org/verify/specialization/${cert_id}'
          }
          $(`#cert_${cert_id}`).append(`<div class="card-body">
            <div class="">
              <label for="code-${cert_id}">Add your certification to your webpage with this HTML: </label>
              <textarea id="code-${cert_id}" class="form-control"><a href="${pdf_url}" target="_blank"><img src="https://certwall.ml/cert/${cert_id}" width="250" alt="Certification ${cert_id}" /></a></textarea>
            </div>
          </div>`)
          /*
          $.get(`/${cert_id}/crawl`, function(json) {
            console.log(json)
            if(json.success) {
              $(`#cert_${cert_id}`).append(`<div class="card-body">  
                <h4 class="card-title">${json.data.course_name}</h4>
                <div class="row">
                  <div class="col-md-6">
                    <div class="card-text">Teacher: ${json.data.teacher_name}</div>
                  </div>
                  <div class="col-md-6">
                    <div class="card-text">School: ${json.data.school_name}</div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6">
                    <div class="card-text">Total Weeks: ${json.data.weeks}</div>
                  </div>
                  <div class="col-md-6">
                    <div class="card-text">Hours Per Week: ${json.data.min_hours_a_week}-${json.data.max_hours_a_week}</div>
                  </div>
                </div>
                <div class="card-text">Complete Date: ${json.data.complete_date}</div>
                <hr/>
                <div class="mt-3">
                  <label for="code-${cert_id}">Add your certification to your webpage with this HTML: </label>
                  <textarea id="code-${cert_id}" class="form-control"><a href="https://coursera.org/verify/${cert_id}" target="_blank"><img src="https://certwall.ml/cert/${cert_id}" width="250" alt="Course Certification for ${json.data.given_name} ${json.data.surname}" /></a></textarea>
                </div>
              </div>`)
              certs.push(cert_id)
              $('#makeWall').removeClass('d-none')
            } else {
              alert(json.error)
            }
          }, 'json')
        */
        } else {
          $('#cert' + certCount).removeClass('is-valid').addClass('is-invalid')
          alert(json.error)
          location.reload()
        }
      }, 'json')
    } else if(cert_id === '') {
      $('#certID').removeClass('is-valid').addClass('is-invalid')
      alert('Certification ID can not be empty!')
    } else {
      $('#certID').removeClass('is-valid').addClass('is-invalid')
      alert('Certification ID invalid!')
    }
  })

  $('#makeWall').click(function() {
    location.href = `/wall?certs=${certs.join('&certs=')}`
  })

  $('#coursera').click(function() {
    $('#dropdownMenuButton').text('Coursera')
    $('#basic-addon').show()
    $('#specialization-addon').hide()
    type = 'coursera'
  })
  $('#courseraSpecialization').click(function() {
    $('#dropdownMenuButton').text('Coursera Specialization')
    $('#basic-addon').hide()
    $('#specialization-addon').show()
    type = 'coursera_specialization'
  })
})
