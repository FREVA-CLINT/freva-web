from django.conf.urls import url, patterns


urlpatterns = patterns('externaluser.views',
    url(r'^register/$', 'external_register', name='external_register')
)
