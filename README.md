# timelapse
Hacks for using an old android phone as a wireless time lapse camera, self powered using a [7W USB solar charger](http://www.amazon.co.uk/gp/product/B00BU38MG0/ref=as_li_tl?ie=UTF8&camp=1634&creative=19450&creativeASIN=B00BU38MG0&linkCode=as2&tag=daybarrcom-21&linkId=7BZTGS5ZNT6V6D7R).

## Requirements

An old Android phone, with camera and wifi. In my case a [HTC Hero](http://en.wikipedia.org/wiki/HTC_Hero). Install the following apps.

* [SSH Server](https://play.google.com/store/apps/details?id=com.icecoldapps.sshserver)
* [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm)

## How to run
Copy the Tasker configuration [userbackup.xml](userbackup.xml) into the Tasker directory at the root of the sdcard of the phone. From within Tasker, import this (Menu, Data, Restore). The config makes use of the [getFormattedDate task](http://tasker.wikidot.com/getformatteddate) for Tasker.

On the server, setup a virtualenv and install the python requirements

    mkvirtualenv timelapse
    pip install -r server/requirements.txt

Run download.py to download all the photos that have been taken, and remove them from the phone.
