import xml.etree.ElementTree as et
import socket
import base64
import time
import numpy


class LightFieldRequest:
    def __init__(self, message=""):
        self.message = message
        self.binary_args = set()
        self.arguments = {}
    def process_request(self, xml_string):
        tree = et.fromstring(xml_string)
        if tree.tag == 'LFRQ':
            self.message = tree[0].text
            for child in tree.iter('arg'):
                if child.get('encoding') == 'base64':
                    self.binary_args.add(child.get('name'))
                self.arguments[child.get('name')] = child.text

    def xml_string(self):
        lfrq = et.Element('LFRQ')
        msg = et.SubElement(lfrq, "msg")
        msg.text = self.message

        for name, value in self.arguments.items():
            arg = et.SubElement(lfrq, "arg")
            arg.set('name', name)
            if name in self.binary_args:
                arg.set('encoding', 'base64')
            arg.text = value
        return et.tostring(lfrq)
    def query_server(self, ip, buffer_size=4096):
        lfs = open_lightfield_server(ip)
        lfs.send(self.xml_string())
        response_xml = lfs.recv(buffer_size)
        lfs.close()
        response_lfrq = LightFieldRequest()
        response_lfrq.process_request(response_xml)
        return response_lfrq

def recv_timeout(the_socket,timeout=0.5):
    the_socket.setblocking(0)
    total_data=[];data='';begin=time.time()
    while 1:
        #if you got some data, then break after wait sec
        if total_data and time.time()-begin>timeout:
            break
        #if you got no data at all, wait a little longer
        elif time.time()-begin>timeout*2:
            break
        try:
            data=the_socket.recv(8192)
            if data:
                total_data.append(data)
                begin=time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    return b''.join(total_data)

def xml_string_for_command(message):
    lfrq = LightFieldRequest(message)
    return lfrq.xml_string()

def open_lightfield_server(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, 13001))
    return s

def query_lightfield_server(ip, command_string, buffer_size=4096):
    lfs = open_lightfield_server(ip)
    lfs.send(xml_string_for_command(command_string))
    response_xml = recv_timeout(lfs)
    lfs.close()
    response_lfrq = LightFieldRequest()
    print(response_xml)
    response_lfrq.process_request(response_xml)
    return response_lfrq

def capture_spectrum(ip):
    lfs = open_lightfield_server(ip)
    lfs.send(xml_string_for_command("CaptureSpectrum"))
    response = lfs.recv(4096) #TODO: check for ack ok
    lfs.close()

    listener = socket.socket()
    listener.bind((socket.gethostname(), 13002))
    listener.listen(5)
    client, addr = listener.accept()
    response_xml = client.recv(4096)
    response_lfrq = LightFieldRequest()
    response_lfrq.process_request(response_xml)
    assert(response_lfrq.message == "SpectrumStored")
    return response_lfrq.arguments['Filename']

def get_current_calibration(ip):
    response_lfrq = query_lightfield_server(ip, "GetCurrentCalibration", 65536)
    assert(response_lfrq.message == "CurrentCalibration")
    data = base64.decodebytes(response_lfrq
                              .arguments['DoubleArray']
                              .encode('UTF-8'))
    return numpy.frombuffer(data, dtype=numpy.float64)

def get_last_spectrum(ip):
    response_lfrq = query_lightfield_server(ip, "GetLastSpectrum", 65536)
    assert(response_lfrq.message == "LastSpectrum")
    data = base64.decodebytes(response_lfrq
                              .arguments['DoubleArray']
                              .encode('UTF-8'))
    return numpy.frombuffer(data, dtype=numpy.float64)

def set_central_wavelength(ip, wavelength_nm):
    command_lfrq = LightFieldRequest("SetCentralWavelength")
    command_lfrq.arguments['Wavelength_nm'] = ("%.4f" % wavelength_nm)
    command_lfrq.query_server(ip)

def test():
    #print(capture_spectrum("192.168.1.87"))
    w = get_current_calibration("192.168.1.87")
    print(w)
    #c = get_last_spectrum("192.168.1.87")
    #cm = numpy.dot(w, c)/numpy.sum(c)
    #skew = numpy.power(numpy.dot(numpy.power(w, 3), c)/numpy.sum(c), 1/3.0)
    #print(cm)
    #print(skew)
    #set_central_wavelength("192.168.1.87", skew)
    #capture_spectrum("192.168.1.87")

if __name__ == '__main__':
    test()