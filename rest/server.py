from flask import Flask
import visa
import re

import numpy as np
from numpy.polynomial.chebyshev import chebval

import request as lfr

from analysis import max_peak_location

app = Flask(__name__)
lightfield_server_ip = "192.168.1.87"

@app.route('/lightfield_available')
def lightfield_available():
    return "true"

@app.route('/set_lightfield_server_ip/<ip>')
def set_lightfield_server_ip(ip):
    global lightfield_server_ip
    lightfield_server_ip = ip
    return "ip set"

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

@app.route('/delay_stage_move_to/<pos>')
def delay_stage_move_to(pos):
    x = int(pos)
    rm = visa.ResourceManager()
    ds = rm.open_resource('ASRL6::INSTR')
    ds.timeout = 60000
    final_position = int(re.split(' ', ds.query('MT %d' % x).rstrip())[1])
    ds.close()
    rm.close()
    return str(final_position)

@app.route('/delay_stage_move_by/<by>')
def delay_stage_move_by(by):
    dx = int(by)
    rm = visa.ResourceManager()
    ds = rm.open_resource('ASRL6::INSTR')
    final_position = int(re.split(' ', ds.query('MB %d' % dx).rstrip())[1])
    ds.close()
    rm.close()
    return str(final_position)

@app.route('/shutter_set_open')
def shutter_set_open():
    rm = visa.ResourceManager()
    ds = rm.open_resource('ASRL3::INSTR')
    ds.read()
    result = ds.query("OPEN")
    ds.close()
    rm.close()
    return result

@app.route('/shutter_set_close')
def shutter_set_close():
    rm = visa.ResourceManager()
    ds = rm.open_resource('ASRL3::INSTR')
    ds.read()
    result = ds.query("CLOSE")
    ds.close()
    rm.close()
    return result


@app.route('/delay_stage_get_position')
def delay_stage_get_position():
    return delay_stage_move_by(0)

@app.route('/power_monitor_calibration/<wavelength>/<voltage>/')
def power_monitor_calibration(wavelength, voltage):
    ps = [ -1.954872514465467656097352744382078527e-02,
        -9.858164527032511337267806084128096700e-01,
        -9.030551056544730559316747076081810519e-02,
        -1.176690008380113228181329532162635587e-01,
        -7.280035069541325454256508464823127724e-02,
        -3.945345662306017076037534252463956363e-02,
        -3.615273166450208575106728403625311330e-02,
         9.788152479007751483042198969997116365e-03,
        -1.456367977705685066991403431302387617e-02,
        -1.786831712872795699387218348874739604e-02,
         2.597734938056468420586320178244932322e-02,
        -2.107763828923307075635662499735190067e-03,
         7.008138732863849161558444933461942128e-03,
         2.152771594326421261689219477375445422e-02,
        -1.331119139869020931432608279010310071e-02,
        -1.377397203478183430880310567090418772e-02,
         5.892610556615005337754986669551726663e-03,
         4.013333930879096900223856891898321919e-03,
        -1.388605295508058999273681699548887991e-03,
        -6.461661481385170711574938984256277763e-04,
         1.965802838584800071083241723712831117e-04,
         5.949925144541367866713593715033425724e-05,
        -1.676361665718153744295687568310881943e-05,
        -2.944515435510320108369441277629263709e-06,
         7.941387605415402886735497592352039931e-07,
         6.088879431605282524011537540614691366e-08,
        -1.605397480549405216611181363393912047e-08]
    #The values below are determined from the dataset associated with the coefficients
    #The fitting is scaled for numerical stability
    w_std = 20.579900281127852
    w_mean = 763.93403214285706
    r_std = 2.9169654028890814e-05
    r_mean = 0.00048691497166276345
    scale_wavelength = (float(wavelength) - w_mean)/w_std
    conversion = chebval(scale_wavelength, ps)
    unscale_r = conversion*r_std + r_mean
    return str(unscale_r*float(voltage))


if __name__ == '__main__':
    app.run(debug=True, host="192.168.1.87")