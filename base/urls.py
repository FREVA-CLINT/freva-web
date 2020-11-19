from django.conf.urls import url, patterns


urlpatterns = patterns('base.views',
    url(r'^$', 'home', name='home'),
    url(r'^logout', 'logout', name='logout'),
    url(r'^wiki', 'wiki', name='wiki'),
    url(r'^contact', 'contact', name='contact'),
    url(r'^restart', 'restart', name='restart'),
    url(r'^ncdump', 'ncdump', name='ncdump'),
    url(r'^freva.cs', 'dynamic_css', name='dynamic_css'),
    #url(r'^shell-in-a-box', 'shell_in_a_box', name='shell_in_a_box'),
    url(r'^forecast-frontend', 'forecast_frontend', name='forecast_frontend')
)
