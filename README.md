# MultiController v0.5

###Summary
Application is design to combine the inputs of a multiple game controllers into a single universal object to be read by server application ran on a Raspberry pi. Server applications use various frameworks that reverse engineer a variety of controllers to connect to console hardware.

The Universal Object can be read by several frameworks, and allows mapping of either a single device, such as keyboard and mouse, or multiple devices to be sent through to consoles.

**Current supported Inputs**
* XInput devices

**Under development**
* Keyboard and mouse

**Current supported consoles**
* Nintendo Switch

###Version updates
**v0.5 Multicontroller**
* Updated application naming from xp1c to Multicontroller
* Updated UI elements to own class
* Updated client to reflect new ui classes
* Added substicks to display and configuration added to ui_config which display position of each stick when multiple inputs are used
* Uploaded to git finally...

**v0.4 UI Update**
* Exported UI configuration to JSON file
* Added Conflict resolution. Sticks update color based on conflict between players using the same stick.
* Stick updates to own function

**v0.3 UI Creation**
* Added Input viewer UI
* Mapped application start to connect button
* Added colors to GameConfig json configuration

**v0.2 Server Updates**
* Server removed hard coded recv and moved to separate thread
* On socket error or server error, server now restarts and listens for new client

**v0.1 Initial Application**
* Socket connection to Raspberry Pi
* Raspberry Pi Function
* Compilation of Multiple XInputs
* Configurable JSON objects for mapping