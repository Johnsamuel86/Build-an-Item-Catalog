
function signInCallback(authResult) {
  if (authResult['code']) {
    // Send the one-time-use code to the server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main page
    $.ajax({
      type: 'POST',
      url: '/gconnect?state=' + state,
      processData: false,
      data: authResult['code'],
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {
        // Handle or verify the server response if necessary.
        if (result) {
        window.location.href = "/catalog";

      } else if (authResult['error']) {
    console.log('There was an error: ' + authResult['error']);
  } else {
        $('#result').html('Failed to make a server-side call. Check your configuration and console.');
         }
      }
  }); } }


gapi.signin.render("GoogleSignIn", {
    'clientid': '689242806893-1hmn08vsqcmofo36t4t6d1ouc98rrdem.apps.googleusercontent.com',
    'callback': signInCallback,
    'cookiepolicy': 'single_host_origin',
    'scope': 'openid email',
    'redirecturi': 'postmessage',
    'accesstype': 'offline',
    'approvalprompt': 'force'
});

