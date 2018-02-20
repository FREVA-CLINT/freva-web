import trim from 'lodash/trim'

/**
 * Needed to send csrf token to django
 * See https://docs.djangoproject.com/en/1.8/ref/csrf/#ajax
 */
export function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie != '') {
    let cookies = document.cookie.split(';');
    cookies.map((cookie) => {
      cookie = trim(cookie);
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
      }
    })
  }
  return cookieValue;
}

export const dateformatter = (isodate) => {
    let newdate = new Date(Date.parse(isodate));
    let d = newdate.getDay()+1;
    let m = newdate.getMonth()+1;
    return `${d<=9 ? '0'+d : d}.${m<=9 ? '0'+m : m}.${newdate.getFullYear()}`
}