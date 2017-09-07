$(function() {
  let certCount = 1
  let html = `<div class="form-group">
    <label for="vert{ind}">Certification {ind}</label>
    <div class="input-group">
      <span class="input-group-addon" id="basic-addon{ind}">https://coursera.org/verify/</span>
      <input type="text" class="form-control" id="cert{ind}" aria-describedby="basic-addon{ind}">
    </div>
  </div>`
  $('#addCert').click(function() {
    certCount++
    $(this).parent().before(html.replace(/\{ind\}/g, certCount))
  })
})