#!/bin/bash
./downloadcovid.sh
./sanitize_data_rate.sh
./sanitize_data_total.sh
./convert_csv_to_json_js.sh
