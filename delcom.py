import sys
import json
import urllib2
import usb.core
import usb.util

# got most of the code from:
# http://sourceforge.net/mailarchive/forum.php?forum_name=pyusb-users&max_rows=25&style=nested&viewmonth=200905
class DelcomUSBDevice(object):
    VENDOR_ID       = 0x0FC5    #: Delcom Product ID
    PRODUCT_ID      = 0xB080    #: Delcom Product ID
    INTERFACE_ID    = 0         #: The interface we use

    def __init__(self):
        self.deviceDescriptor = DeviceDescriptor(self.VENDOR_ID,
                                                 self.PRODUCT_ID,
                                                 self.INTERFACE_ID)
        self.device = self.deviceDescriptor.getDevice()
        if self.device:
            print 'Found Delcom Device'
            self.conf = self.device.configurations[0]
            self.intf = self.conf.interfaces[0][0]
        else:
            print >> sys.stderr, "Cable isn't plugged in"
            sys.exit(0)


    def open(self):
        try:
            self.handle = self.device.open()
            self.handle.detachKernelDriver(0)
        except usb.USBError, err:
            if str(err).find('could not detach kernel driver from interface') >= 0:
                print 'The in-kernel-HID driver has already been detached'
            else:
                print >> sys.stderr, err
        #self.handle.setConfiguration(self.conf)
        self.handle.claimInterface(self.intf) # Interface 0


    def close(self):
        try:
            self.handle.releaseInterface()
            print 'released interface'
        except Exception, err:
            print >> sys.stderr, err


    def getManufactureName(self):
        return self.handle.getString(self.device.iManufacturer,30)


    def getProductName(self):
        return self.handle.getString(self.device.iProduct,30)


    def writeData(self, data):
        """ Write data to device:
                0x21   = REQ_TYPE: DIR = Host to Device
                         REQ_TYPE: TYPE = Class
                         REQ_TYPE: REC = Interface
                0x09   = REQUEST: HID-Set Report
                data   = Command sent to Delcom device
                0x0365 = VALUE: 0x65 = ReportID = 101 = MajorCMD
                         VALUE: 0x03 = Report Type = Feature Report
                0x0000 = Interface number = 0
                100    = timeout 100mS
        """
        sent = self.handle.controlMsg(0x21, 0x09, data, 0x0365, 0x0000, 100)
        print 'Bytes written %s', sent



class DeviceDescriptor(object):
    def __init__(self, vendor_id, product_id, interface_id):
        '''
        Constructor
        '''
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.interface_id = interface_id

    def getDevice(self):
        busses = usb.busses()
        for bus in busses:
            for device in bus.devices:
                if device.idVendor == self.vendor_id and \
                   device.idProduct == self.product_id:
                    return device
        return None

class Controller():
    TEAMCITY_URI = 'simbuild'
    SIGNALS = {
        "green": {
            "on": "\x65\x0C\x01\x00\x00\x00\x00\x00",
            "off": "\x65\x0C\x00\x01\x00\x00\x00\x00"
        },
        "red": {
            "on": "\x65\x0C\x02\x00\x00\x00\x00\x00",
            "off": "\x65\x0C\x00\x02\x00\x00\x00\x00"
        },
        "blue": {
            "on": "\x65\x0C\x04\x00\x00\x00\x00\x00",
            "off": "\x65\x0C\x00\x04\x00\x00\x00\x00"
        }
    }

    def __init__(self, device):
        self.device = device

    def __turn_off__(self):
        self.device.open()
        self.device.writeData(self.SIGNALS['red']['off'])
        self.device.writeData(self.SIGNALS['green']['off'])
        self.device.writeData(self.SIGNALS['blue']['off'])
        self.device.close()

    def turn_on(self, color='green'):
        # print 'Manufacturer: ', self.device.getManufactureName()
        # print 'Product: ', self.device.getProductName()
        self.__turn_off__()
        self.device.open()
        self.device.writeData(self.SIGNALS[color]['on'])
        self.device.close()

    def __is_broken__(self, build_id):
        request = urllib2.Request(
            'http://%s/guestAuth/app/rest/buildTypes/id:%s/builds' % (self.TEAMCITY_URI, build_id),
            headers = {'Accept': 'application/json'}
        )
        builds = json.loads(urllib2.urlopen(request).read())

        return str(builds['build'][0]['status']) == 'FAILURE'

    def has_failure(self, build_ids):
        failed = False

        for build_id in build_ids:
            failed |= self.__is_broken__(build_id)

        return failed

def main():
    controller = Controller(DelcomUSBDevice())
    if controller.has_failure(sys.argv[1:]):
        controller.turn_on('red')
    else:
        controller.turn_on('green')

if __name__ == '__main__': main()
