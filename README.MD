# sensorPi - WIP
My OCR Computer Science A Level project
the goal is to create a selfhosted (RPi) instance of a CO2 sensor with facilities to store and present readings
## features
- a display for adhoc data visualisation (showing latest measurements) – teaches basic python hardware interfacing, use of libraries, basic systemd service and interrupt signal management
- a local sqlite database to store the readings with a timestamp for reference – teaches basic python sqlite interfacing
- **TODO:** a static webpage which visualises data through charts and graphs – nothing learnt yet (haven't started xDD)
- **TODO:** options to request maximum/minimum – both individual values and timespans (either simple SQL ORDER BY or sorting algs) e.g. the hour with worst CO2 ppm
- **TODO (possibly):**  statistical analysis of the data – st.d., mean and median, possible correlations
