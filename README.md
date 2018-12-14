# ChE436-project
Repository for ChE436 group project. Consists of a small enclosure where the temperature is reported and regulated by a Rasberry Pi with Python. 

## Potential Future Work
- Add ability to 'auto-tune' PID and FOPDT parameters for new heater and box sizes
 

## Current Results
- Doublet test:  
    - Kp: 0.14501294865265488
    - tau_p: 159.4251614964272
    - thetaP: 124.9997
- Singlet(?) test:
    - Kp: 0.1784425264458022
    - tau_p: 250.53173824851896
    - thetaP: 70.25532426084045
    - error: 177.71500265128566
 - PID params (based on doublet):
    - Kc: 1.44
    - tau_I: 221.925
    - tau_D: 44.898
 - Optimized PID params:
    - Kc: 2.0
    - tau_I: 75.0
    - tau_D: 0.0
