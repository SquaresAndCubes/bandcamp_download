# bandcamp_download

Welcome to Bandcamp Download project.

This project is for downloading users shows from their Bandcamp Collection in an automated manner.

Currently FLAC is the only format that gets downloaded. Will be adding more options later.

Requirements to use Bandcamp Download are below. Don't worry I will instruct on how to get these set up.

- Windows 10 or 11
- Python 3.10.9
- Installation of Python dependencies that are part of the requirements.txt file
- Google Chrome
- A Hard Drive path with ample space such as C:\STS9
- Sector 9 Mindset :)

Instructions:

1. Download and Install Python 3.10.9 to your system with this link: 
https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe

- Check box "Add python.exe to PATH"
- Choose "Customize Installation"
- Click Next
- Check box "Add Python to environment variables" and "Precompile standard library"
- Click Install

2. Open Google Chrome and login to your Bandcamp account

3. Download Bandcamp Download app zip file from this link:
https://github.com/SquaresAndCubes/bandcamp_download/archive/refs/heads/master.zip

- Unzip the file to any directory you like for example: C:\Users\some_user\Downloads\bandcamp_download-master

- Navigate to the unzipped directory in a Windows Command Line Prompt (not PowerShell)

- Issue the command as below and you will see Python packages install --> wait for complete

C:\Users\some_user\Downloads\bandcamp_download-master> python -m pip install requirements.txt

4. Now you are ready to run the app!

- From same command line issue below command with desired parameters. 
- '-p' is the path you want files to get saved; default is C:\STS9
- '-q' is how many shows you want to download; default is 1 show

**Example command to start the download process.**

C:\Users\some_user\Downloads\bandcamp_download-master> python bandcamp_download.py -p C:\STS9 -q 10

After you issue the start command you will see:
- Initializing phase will install Google Chrome web driver

- Possibly a couple errors you can ignore about cache

- Then you should see something like below and it will take a few minutes to complete.
Initializing squaresandcubes's collection from ---> URL: https://bandcamp.com/squaresandcubes
Finding all shows in user squaresandcubes's collection. Please wait...

- Then you should see something like below and it should stop and wait for you to press enter to start downloading:

Gathering show download URLs...
---> Found 845 shows in squaresandcubes's collection for download
!! User has provided a show quantity. Limiting scope to 1 shows !!
Bandcamp Download initialization completed !!
!! Press Enter to Download 1 Shows !!

It will start to download shows and it will print out the name of each show as it downloads.
They come in .zip format so you will have to navigate to the directory you targeted for download and unzip each show to listen.

Thats it!! You did it!! Enjoy :)

