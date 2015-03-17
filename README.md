# timelapse
Hacks for using an old android phone as a wireless time lapse camera, powered with a [solar charger](http://www.amazon.co.uk/gp/product/B00BU38MG0/ref=as_li_tl?ie=UTF8&camp=1634&creative=19450&creativeASIN=B00BU38MG0&linkCode=as2&tag=daybarrcom-21&linkId=7BZTGS5ZNT6V6D7R).

## Requirements

* An old Android phone, with camera and wifi. In my case a [HTC Hero](http://en.wikipedia.org/wiki/HTC_Hero).
* A server capable of running python on the same LAN as the phone.
* A power source. In my case this hack must be self-sufficient as there is no access to mains power. The [7W USB solar charger](http://www.amazon.co.uk/gp/product/B00BU38MG0/ref=as_li_tl?ie=UTF8&camp=1634&creative=19450&creativeASIN=B00BU38MG0&linkCode=as2&tag=daybarrcom-21&linkId=7BZTGS5ZNT6V6D7R) from PortaPow is ideal for this job.
* Some string, glue, tape and other bodgey hardware pieces to hold the phone in the appropriate position, give a clear view for the camera, but somehow protect it from the British weather.

## Setup

The phone automatically takes a photo every 2 minutes, during the required daylight hours. Photos are saved to the SD card with a timestamped file name.

A server on the LAN (raspberry pi in my garage) continually attempts to connect to the phone and download the photos from it. Once a photo is safely stored on the server, it is removed from the phone so the SD card doesn't fill up.

The phone's WiFi is only activated during daylight, when the phone is being charged by the solar panel. So server must cope with losing the connection at any time.

At night, no photos are being taken, the WiFi on the phone turns off and the SSH server shuts down, conserving power until the sun starts charging again the next day. The battery in the phone should be sufficient to see it through the dark zone, especially if you remove the SIM card and disable mobile networks (recommended for security reasons anyway).

### Phone

#### Tasker

For taking photos, activating/deactivating wifi and monitoring the battery charge level.

Install [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm) from the Play Store.

Copy the Tasker configuration [userbackup.xml](userbackup.xml) into the Tasker directory at the root of the sdcard of the phone. From within Tasker, import this (Menu, Data, Restore). The config makes use of the [getFormattedDate task](http://tasker.wikidot.com/getformatteddate) for Tasker.

#### SSH Server

For the server to use to download and delete photos from the phone.

Install [SSH Server](https://play.google.com/store/apps/details?id=com.icecoldapps.sshserver) from the Play Store.

In the SSH Server app, add a connection and user with access to the SD card (`/mnt/sdcard`) and set it to start automatically at boot, and when the SSID of your wifi network is available.

### Server

On the server, setup/activate a virtualenv and install the python requirements

    mkvirtualenv timelapse
    pip install -r server/requirements.txt

Run `server/download.py` to download all the photos that have been taken, and remove them from the phone.
