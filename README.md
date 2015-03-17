# timelapse
Hacks for using an old android phone as a wireless time lapse camera, powered with a [solar charger](http://www.amazon.co.uk/gp/product/B00BU38MG0/ref=as_li_tl?ie=UTF8&camp=1634&creative=19450&creativeASIN=B00BU38MG0&linkCode=as2&tag=daybarrcom-21&linkId=7BZTGS5ZNT6V6D7R).

## Requirements

* **The Camera** - An Android device, with camera and WiFi.
    * In my case a 2010 era [HTC Hero](http://en.wikipedia.org/wiki/HTC_Hero) running [CyanogenMod 7](http://www.cyanogenmod.org/).
* **The Server** - Any mains powered device capable of running python and on the same LAN as the Camera's WiFi.
    * In my case, a [Raspberry Pi Model B](http://www.raspberrypi.org/products/model-b/) in my garage.

If the Camera is going to be outside, as in my case, you will also need:

* A power source for the Camera that is convenient for its mounting location.
    * In my case, there is no access to mains power at the proposed site. The [7W USB solar charger](http://www.amazon.co.uk/gp/product/B00BU38MG0/ref=as_li_tl?ie=UTF8&camp=1634&creative=19450&creativeASIN=B00BU38MG0&linkCode=as2&tag=daybarrcom-21&linkId=7BZTGS5ZNT6V6D7R) from PortaPow is ideal for this job, making the Camera system self-sufficient.
* A weatherproof enclosure.
    * In my case, probably some tupperware, string, glue, tape and other bodgey hardware things to hold the phone in the appropriate position, give a clear view for the camera, but somehow protect it from the British weather.
    * TODO

## Setup

The Camera automatically takes a photo every 2 minutes, during the required daylight hours. Photos are saved to the SD card with a timestamped file name.

The Server continually attempts to connect to the Camera and download the photos from it. Once a photo is safely stored on the Server, it is removed from the Camera so the SD card doesn't fill up.

The Camera's WiFi is only activated during daylight, when the Camera is being charged by the solar panel. So the Server must cope with losing the connection to the Camera at any time.

At night, the Camera stops taking photos, turns off the WiFi and stops the SSH Server, thus conserving power until the sun starts charging it again the next day. The battery in the Camera should be sufficient to see it through the dark zone, especially if you remove the SIM card and disable mobile networks (where applicable - recommended for security reasons anyway).

### Camera

#### Tasker

For taking photos, activating/deactivating WiFi and monitoring the battery charge level.

Install [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm) from the Play Store.

Copy the Tasker configuration [userbackup.xml](userbackup.xml) into the Tasker directory at the root of the sdcard of the Camera. From within Tasker, import this (Menu, Data, Restore).

Credit: My Tasker config makes use of this [getFormattedDate task](http://tasker.wikidot.com/getformatteddate) for Tasker.

#### SSH Server

For the Server to connect to so it can download and delete photos from the Camera.

Install [SSH Server](https://play.google.com/store/apps/details?id=com.icecoldapps.sshserver) from the Play Store.

In the SSH Server app, add a connection and user with access to the SD card (`/mnt/sdcard`) and set it to start automatically at boot, and when the SSID of your WiFi network is available.

### Server

On the Server, setup/activate a virtualenv and install the python requirements

    mkvirtualenv timelapse
    pip install -r server/requirements.txt

Run `server/download.py` to download all the photos that have been taken, and remove them from the Camera.
