from flask import Flask
import flask
import request as lfr
from analysis import max_peak_location

app = Flask(__name__)
lightfield_server_ip = "192.168.1.87"

@app.route('/set_lightfield_server_ip/<ip>')
def set_lightfield_server_ip(ip):
    global lightfield_server_ip
    lightfield_server_ip = ip

@app.route('/cap_spec')
def cap_spec():
    global lightfield_server_ip
    spec_path = lfr.capture_spectrum(lightfield_server_ip)
    return spec_path

@app.route('/wavelength_at_max')
def wavelength_at_max():
    w = lfr.get_current_calibration(lightfield_server_ip)
    lfr.capture_spectrum(lightfield_server_ip)
    i = lfr.get_last_spectrum(lightfield_server_ip)
    max_w, max_i = max_peak_location(w, i)
    return ("%.3f" % max_w)

if __name__ == '__main__':
    app.run(debug=True, host="192.168.1.95")