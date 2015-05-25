AFT - Automated Flasher & Tester- Core package - Documentation
==============================================================

Overview
--------
AFT is a tool for automated provisioning and testing.
Its goal is to both standardize and simplify the testing on a variety
of devices, while keeping minimal the cost and complexity of the setup.
In particular, it strives to use only inexpensive off-the shelf
HW components and to keep one single configuration that can be used
by both large testing farms and individual testers/developers.



How it works
------------
At very high level, the tool receives as input the name of a file
containing the SW image to be tested and a test plan.

It then proceeds to assess if the SW image can be deployed on one of
the devices connected to the testing harness (the machine running AFT).

If the image is supported, the tester will attempt to reserve a 
compatible device and, once the device becomes available, deploy the
image.

If the image deploys successfully and can also boot the device, then
the system will run the requested test plan.

The design is modular, so that if one needs to address a configuration
that is not supported, it will be possible to support it with minimal
intervention.

This specific module is not meant for standalone use.
Instead, it will be pulled in as dependency, when installing other
pacakges.


Key plugins required
--------------------

* device plugin
This represents the device under test (DUT) and provides means for:
 - deploying new SW images
 - accessing the device and executing commands remotely.

* cutter plugin
This represents the means for (un)powering the DUT and forcing it to
restart, even when it is totally locked up, due to some SW bug.

* test plugin
This represents a test case to execute on the device.
