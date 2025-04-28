@echo off
echo Running Helios Tests...
cd ..
python -m pytest tests/test_helios.py tests/test_socket_communication.py tests/test_ui.py -v
echo Test run complete! 