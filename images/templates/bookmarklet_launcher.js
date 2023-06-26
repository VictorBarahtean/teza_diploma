(function(){
    if (window.myBookmarklet !== undefined){
        myBookmarklet();
    }
    else {
        document.body.appendChild(
        document.createElement('script')
        ).src='https://c232-178-168-36-70.ngrok.io/static/js/bookmarklet.js?r=' +
        Math.floor(Math.random()*99999999999999999999);
    }
   })();