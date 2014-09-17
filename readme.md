#Dropbox Phone Camera Folder Downloader
Dropbox Phone Camera Folder Downloader is a simple but reasonably robust Python script to download the folder which automatically stores photos taken on your phone if you have that facility enabled.

##Instructions
First you will need to setup a Dropbox application.

###Setting Up a Dropbox Application
To set up your Dropbox application, go to the [Dropbox developers portal](https://www.dropbox.com/developers) and log in with your Dropbox credentials if required.  From there, click the 'App Console' link on the left and choose to create a new Dropbox API app. Choose the files and datastores option under the data type your application needs to access, choose NOT to limit your app to its own folder and choose the option to allow your app to access all file types. Finally, choose a name for your app, preferably something meaningful, and you are done with your Dropbox application setup.  Just make a note of your App Key and App Secret as you will need them to configure the script in a bit.

###Installing Required Modules
You may need to install the Dropbox Python module.

```
pip install dropbox
```

###Complete the Configuration File
Make a copy of the dropboxpics.cfg.sample file and name it dropboxpics.cfg

Add the application key and secret you obtained from Dropbox as indicated to the dropboxpics.cfg file

###Running the Script
```
python dropboxpics.py
```
