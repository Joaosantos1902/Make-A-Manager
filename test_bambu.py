import bambulabs_api as bl
import time


import time
import bambulabs_api as bl

IP = ''
SERIAL = ''
ACCESS_CODE = ''

if __name__ == '__main__':
    print('Starting bambulabs_api example')
    print('Connecting to BambuLab 3D printer')
    print(f'IP: {IP}')
    print(f'Serial: {SERIAL}')
    print(f'Access Code: {ACCESS_CODE}')

    # Create a new instance of the API
    printer = bl.Printer(IP, ACCESS_CODE, SERIAL)

    # Connect to the BambuLab 3D printer
    printer.connect()

    time.sleep(2)

    # Get the printer status
    status = printer.get_state()
    print(f'Printer status: {status}')

    filename = printer.get_file_name()
    print(f'Current file name: {filename}')

    # Disconnect from the Bambulabs 3D printer
    printer.disconnect()