import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select


class EvaluationSystemWeb(unittest.TestCase):
    
    id_to_test = '13056'
    
    def logout_user(self):
        # if user is logged, log him out
        try:
            elem = self.driver.find_element_by_link_text('logout ('+self.username+')')
            elem.click()
        except NoSuchElementException:
            pass  
    
    def login_user(self):
        try:
            elem = self.driver.find_element_by_link_text('logout ('+self.username+')')
        except:
            elem = self.driver.find_element_by_name('user')
            elem.send_keys(self.username)
            elem = self.driver.find_element_by_name('password')
            elem.send_keys(self.pw+Keys.RETURN)
            time.sleep(2)
            self.assert_('Evaluation System' in self.driver.title)    

    def click_link(self, linktext):
        try:
            elem = self.driver.find_element_by_link_text(linktext)
            elem.click()    
        except NoSuchElementException:
            self.fail("Can't find link text %s" % linktext)
    
    def start_tool(self, tool, caption=''):
        self.driver.find_element_by_id('runButton').click()
        elem = self.driver.find_element_by_id('password_temp')
        elem.clear()
        elem.send_keys(self.pw)
        self.driver.find_element_by_id('submit_analysis').click()        
        if caption == '':
            self.assertEqual(tool+' results - Evaluation System', self.driver.title, 'Tool could not be started')
        else:
            self.assertEqual(caption+' ('+tool.upper()+') results - Evaluation System',
                             self.driver.title, 'Tool could not be started')
              
    def __init__(self, *args, **kwargs):
        
        super(EvaluationSystemWeb, self).__init__(*args, **kwargs)
        self.driver = webdriver.Firefox()
        self.driver.desired_capabilities['acceptSslCerts'] = True 
        self.driver.setAcceptUntrustedCertificates = True 
        self.driver.setAssumeUntrustedIssueer = False

        self.username = username
        self.pw = pw
        
    def __del__(self, *args, **kwargs):
        self.driver.close()
    
    def setUp(self):
        self.driver.get('https://www-miklip.dkrz.de/')
        self.driver.implicitly_wait(10)  # seconds
        self.login_user()
        
    def test_login(self):
        self.driver.get('https://www-miklip.dkrz.de/')
        self.assert_('Evaluation System' in self.driver.title)
        # test login process
        self.logout_user()
        elem = self.driver.find_element_by_name('user')
        elem.send_keys(self.username)
        elem = self.driver.find_element_by_name('password')
        elem.send_keys(self.pw+Keys.RETURN)
        self.assert_('Evaluation System' in self.driver.title)
        # raises NoSuchElementException if not logged in
        try:
            elem = self.driver.find_element_by_link_text('logout ('+self.username+')')
        except NoSuchElementException:
            self.fail('Login failed')
            
    def test_data_browser(self):
        self.driver.get('https://www-miklip.dkrz.de/solr/data-browser/')
        self.assert_('Data Browser - Evaluation System' in self.driver.title)
        self.click_link('project')
        self.driver.implicitly_wait(10)  # seconds
        self.click_link('baseline0')
        elem = self.driver.find_element_by_css_selector('span.ncdump')
        elem.click()

        # test ncdump functionality
        elem = self.driver.find_element_by_id('password_temp')
        elem.send_keys(self.pw+Keys.RETURN)
        elem = self.driver.find_element_by_css_selector('pre')
        elem = self.driver.find_element_by_class_name('close')
        elem.click()

        # test variable title
        self.driver.find_element_by_class_name('facet_clear').click()
        self.click_link('variable')
        elem = self.driver.find_element_by_link_text('tas')
        self.assertEqual('Near-Surface Air Temperature', elem.get_attribute('data-original-title'))
        
    def test_tools(self):
        import time

        self.driver.get('https://www-miklip.dkrz.de/plugins/')
        self.assertEqual('Tools - Evaluation System', self.driver.title)
        
        # tool_to_check
        tool = 'MoviePlotter'
        elem = self.driver.find_element_by_partial_link_text(tool)
        elem.click()
        self.assertEqual(tool + ' - Evaluation System', self.driver.title)
        
        self.click_link('Start analysis')
        self.assertEqual(tool + ' setup - Evaluation System', self.driver.title)
        
        # test movieplotter form
        self.driver.find_element_by_id('id_input_solr').click()
        
        solr_dict = dict(experiment='hadcrut3v')

        self.driver.find_element_by_class_name('VS-search-inner').click()
        self.driver.implicitly_wait(10)  # seconds
        for key, val in solr_dict.iteritems():
            elem = self.driver.find_element_by_partial_link_text(key).click()
            elem = self.driver.find_element_by_partial_link_text(val).click()   
        time.sleep(5)
        elem = self.driver.find_element_by_class_name('VS-search-inner')
        elem.send_keys(Keys.TAB+Keys.SPACE)
        self.driver.find_element_by_id('solr_select_file').click()

        elem = self.driver.find_element_by_id('id_seldate')
        elem.clear()
        elem.send_keys('2010-01-0100:00:00,2010-12-3122:00:00')
        
        # add caption to result
        testcaption = 'test case caption'
        self.driver.find_element_by_id('id_caption').send_keys(testcaption)
        
        self.start_tool('MOVIEPLOTTER', testcaption)
        
        # test caption
        self.assertEqual(testcaption+' ('+tool.upper()+')', self.driver.find_element_by_id('result_caption').text,
                         'Setting caption failed')
        
        # cancel job
        self.driver.find_element_by_id('cancelButton_').click()
        elem = self.driver.find_element_by_id('password_temp')
        elem.clear()
        elem.send_keys(self.pw)
        self.driver.find_element_by_id('submitCancelBtn').click()
        try:
            self.driver.find_element_by_link_text('No Results (Process status: broken)')
        except:
            self.fail('Job is not cancelled')
        
        # rerun configuration
        self.driver.find_element_by_id('config_button').click()
        self.assertEqual(tool+' setup - Evaluation System', self.driver.title, 'Edit config not loaded')
        
        self.start_tool('MOVIEPLOTTER')
        
    def test_results(self):
        self.driver.get('https://www-miklip.dkrz.de/history/'+self.id_to_test+'/results/')
        self.assertEqual('MOVIEPLOTTER results - Evaluation System', self.driver.title,
                         'Cant find result (title changed?)')
        
        # test share results
        self.click_link('Share Results')
        time.sleep(2)
        elem = self.driver.find_element_by_class_name('select2-choices')
        # send mail to 'b324057'
        self.driver.execute_script("$('#mail_to_field').val('"+self.username+"');")
        self.driver.find_element_by_id('sendBtn').click()
        # WORKAROUND OPEN DIALOG AGAIN
        self.click_link('Share Results')
        time.sleep(5)  # wait until mail is sent
        self.assertEqual(self.driver.find_element_by_css_selector('div#status_div > p').text,
                         'Sent to Sebastian Illing', 'Mail not sent')
        self.driver.find_element_by_class_name('close').click()
        
        # test set caption
        self.click_link('Set Caption')
        time.sleep(2)
        elem = self.driver.find_element_by_id('caption_field')
        elem.clear()
        elem.send_keys('test caption')
        self.driver.find_element_by_id('applyBtn').click()
        time.sleep(1)
        self.assertEqual('test caption (MOVIEPLOTTER)', self.driver.title, 'Cant set caption')
        self.click_link('Set Caption')
        time.sleep(2)
        self.click_link('Default caption:')
        self.driver.find_element_by_id('applyBtn').click() 
        time.sleep(1)
        self.assertEqual('test caption (MOVIEPLOTTER)', self.driver.title, 'Cant set caption')
        
        # test notes
        self.driver.find_element_by_partial_link_text('Notes').click()
        time.sleep(1)
        self.click_link('New')
        elem = self.driver.find_element_by_id('textarea_new')
        elem.send_keys('Super Results!')
        self.click_link('Save')
        time.sleep(3)
        # edit note
        elem = self.driver.find_element_by_link_text('Edit')
        note_id = elem.get_attribute('id')
        note_id = note_id.split('_')[-1]
        self.driver.find_element_by_id('btn_edit_'+note_id).click()
        time.sleep(1)
        elem = self.driver.find_element_by_id('textarea_'+note_id)
        elem.clear()
        elem.send_keys('Doch nicht so geil...')
        self.click_link('Save')
        time.sleep(1)
        self.driver.find_element_by_id('btn_delete_'+note_id).click()

    def test_history(self):
        
        self.driver.get('https://www-miklip.dkrz.de/history/')
        self.assertEqual('History - Evaluation System', self.driver.title, 'Cant open history')
        self.driver.implicitly_wait(10)  # seconds
        # get latest result id
        elem = self.driver.find_element_by_css_selector('tbody tr')
        hist_id = elem.get_attribute('id')
        
        # delete element
        self.driver.find_element_by_id('cb_'+hist_id).click()
        self.click_link('Delete')
        # filter deleted elements
        select = Select(self.driver.find_element_by_css_selector('select#filter_flag'))
        select.select_by_value('3')
        btn = self.driver.find_element_by_css_selector('form button')
        btn.click()
        # undelete element
        self.driver.find_element_by_id('cb_'+hist_id).click()
        self.click_link('Undelete')
        # filter undeleted
        select = Select(self.driver.find_element_by_css_selector('select#filter_flag'))
        select.select_by_value('-1')
        btn = self.driver.find_element_by_css_selector('form button')
        btn.click()
        
if __name__ == "__main__":
    import getpass
    print "Username:",
    username = raw_input()
    pw = getpass.getpass('Password:')
    unittest.main()        