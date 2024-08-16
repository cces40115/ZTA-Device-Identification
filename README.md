# ZTA-Device-Identification
Regarding the Taiwanese Zero Trust Architecture (ZTA) certification, the second phase

The following code currently uses Python to retrieve the corresponding device identification information.

"The code cannot currently be executed on Windows Server because it triggers an official security policy warning."

How to use:
Install PyInstaller:
You can install PyInstaller using pip. Open your Command Prompt or Terminal and run:
pip install pyinstaller

Package Your Python Script:
Assuming your Python script is named my_script.py, you can package it using the following command:
pyinstaller --onefile my_script.py

The --onefile option tells PyInstaller to bundle everything into a single executable file. If you don’t use this option, PyInstaller will create a directory with multiple files.

Locate the Executable:
Once the packaging process is complete, you can find the generated executable file in the dist directory. For example, you will find my_script.exe inside the dist folder.

Test the Executable:
Make sure to test the generated executable on different machines to ensure it works correctly.

The output of the sample code:
Output Results：
1. BIOS Info:
    Manufacturer:
    SerialNumber:

2. CPU Info:
    Name:
    ProcessorId:
    NumberOfCores:

3. Disk Info:
    Model:
    Size:
    Partitions:
    FileSystems:

4. Memory Info:
    TotalSize: 
    MemoryModel: 
    MemorySpeed: 

5. OS Info:
    OSName:
    Version:
    BuildNumber:

6. Network Info:
    HostName:
    AzureADDomain:
    LocalADDomain:
    Location:
    CurrentIP:
    IP:
    Netmask:
    Gateway:
    MAC address:
    Bluetooth MAC address:
