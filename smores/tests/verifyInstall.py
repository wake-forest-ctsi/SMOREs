# Python Lib Modules
import subprocess
import sys
import os
import logging
import time
# Community Modules
# SMOREs Internal Imports
import os

cui_tests = {'RXNORM': ['161'], 'NDC': ['0004-0038-22'], 'SNOMED': []}

_c, _ = os.path.split(os.path.dirname(os.path.abspath(__file__)))
_c1, _ = os.path.split(_c)
_p = sys.path
sys.path.insert(0, _c1)
sys.path.insert(1, _c.join('api.py'))
_p = sys.path

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
controlled_failure = 'muhnamena [Should Not Be Found]'
required_packages = ['PyYAML','tqdm','requests','requests-cache','python-dateutil','pandas','numpy', controlled_failure]

error_log_path = os.path.join(_c, 'logs', 'install.log')
logging.basicConfig(filename=error_log_path,
                                format='%(asctime)s %(funcName)-12s %(levelname)-8s %(message)s',
                                filemode='w', level=logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.CRITICAL)
formatter = logging.Formatter('%(levelname)-10s %(message)s')
console.setFormatter(formatter)

logging.getLogger('').addHandler(console)
print('Errors Will Be Recorded Under: {0}'.format(error_log_path))
print('Confirming Package Installs')
time.sleep(.05)

install_tests = {'lib': None, 'rxnav': None, 'rxndc': None, 'fda': None, 'umls': None, 'testFile': None}

for package in required_packages:
    if package not in installed_packages:
        logging.critical('Module Not Found : {0}'.format(package))
        install_tests['lib'] = False if package != controlled_failure else install_tests['lib']
    else:
        logging.info('Module Found : {0}'.format(package))

    install_tests['lib'] = True if install_tests['lib'] is None else install_tests['lib']

if not install_tests['lib']:
    print('\nLibrary Checks Failed, Aborting Additional Tests Due to Expected Failures')
else:
    try:
        from smores.api import RXNAV, openFDA, RXNDC
    except ModuleNotFoundError as err:
        logging.critical('Failed to Load API Module : {0}'.format(err))
        print('\nAPI Module Load Failed, Aborting API Tests Due to Expected Failures')
    else:
        try:
            rxn = RXNAV()
            test_id = 1
            for test_cui in cui_tests['RXNORM']:
                success, results = rxn.get_cui_status(test_cui)
                if success:
                    logging.info(results)
                    logging.info('RxNav Test {0} Successful'.format(test_id))
                    test_id += 1
                else:
                    install_tests['rxnav'] = False
                    logging.critical('RxNav Test {0} Failed'.format(test_id))
            install_tests['rxnav'] = True if install_tests['rxnav'] is None else install_tests['rxnav']
        except ValueError:
            logging.critical('RxNav Test Failed to Initialize')

        try:
            test_id = 1
            fda = openFDA()
            for test_cui in cui_tests['NDC']:
                results = fda.get_ndc_base(test_cui)
                if results:
                    logging.info(results)
                    logging.info('openFDA Test {0} Successful'.format(test_id))
                    test_id += 1
                else:
                    logging.critical('openFDA Test {0} Failed'.format(test_id))
                    install_tests['rxnav'] = False

            install_tests['fda'] = True if install_tests['fda'] is None else install_tests['fda']
        except ValueError:
            logging.critical('openFDA Test Failed to Initialize')

        try:
            test_id = 1
            rxn = RXNDC()
            for test_cui in cui_tests['NDC']:
                success, results = rxn.get_cui_status(test_cui)
                if success:
                    logging.info(results)
                    logging.info('RXNav NDC Test {0} Successful'.format(test_id))
                    test_id += 1
                else:
                    logging.critical('RXNav NDC Test {0} Failed'.format(test_id))
                    install_tests['rxndc'] = False
            install_tests['rxndc'] = True if install_tests['rxndc'] is None else install_tests['rxndc']
        except ValueError:
            logging.critical('RXNav NDC Test Failed to Initialize')


print('\n----------\nInstallation Test Results\n----------\n')
for key in install_tests.keys():
    print_key = key.upper()

    if install_tests[key]:
        print_result = 'SUCCESS'
    elif install_tests[key] is None:
        print_result = 'INCOMPLETE'
    else:
        print_result = 'FAILED'
    print('{0} Results : {1}'.format(print_key, print_result))

print('\n\nTests Marked as "FAILED" Will Have Details Recorded in {0}'.format(error_log_path))
print('Tests Marked as "INCOMPLETE" Were Not Executed Due to Preceding Failure or Were Disabled')