@echo off
echo Committing SIRIUM v1.0.1.0 - TIME PARSING WORKING!...

git add sirium_to_ssim_converter.py
git add version.py
git add test_time_parsing.py
git add test_full_ssim_with_times.py
git add show_times_example.py
git commit -m "Version 1.0.1.0: TIME PARSING WORKING PERFECTLY!

- Fix time parsing for SFO format (1730 -> 17:30) in parse_time_sfo()
- Add support for float/int time values from Excel
- Handle all time formats: HHMM, HMM, H, with proper zero padding
- Times now appear correctly in SSIM output
- Example: DEL02350235+0530  SFO17301730-0800
- Add comprehensive time parsing tests"

git push

echo Commit completed!
pause
