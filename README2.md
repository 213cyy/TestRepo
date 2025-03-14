# HiveWE
HiveWE is a Warcraft III World Editor (WE) that focusses on speed and ease of use. 
It improves massively on the vanilla WE, especially for large maps where the regular World Editor is often too slow and clunky.


[Thread on the Hiveworkshop](https://www.hiveworkshop.com/threads/introducing-hivewe.303183/)

Some of the benefits over the vanilla WE:
- Faster loading
- Faster rendering
- Faster editing


## Features

- Edit the terrain
![HiveWE Screenshot](/Screenshots/HiveWE.png)
- Advanced Object Editor
![HiveWE Screenshot](/Screenshots/ObjectEditor.png)



## Build Instructions

0. Requires Visual Studio 17.7 or higher (C++20 modules)
1. Clone HiveWE somewhere 
`git clone https://github.com/stijnherfst/HiveWE.git`
2. Clone [vcpkg](https://github.com/microsoft/vcpkg) somewhere central (eg. "C:/")
`git clone https://github.com/Microsoft/vcpkg.git`
3. Run vcpkg/bootstrap-vcpkg.bat
4. Add an environment variable to your system:
- `VCPKG_ROOT`: the location where vcpkg is installed (e.g. "C:\vcpkg")
5. Open Visual Studio as an **Administrator** and using the open folder button to open the HiveWE folder. (**Administrator required** for creating a symbolic link on Windows)
6. Dependencies will be automatically compiled, might take about 15-20 minutes (mostly due to Qt)

**Done**

If you run into any issues then feel free to contact me at HiveWorkshop (eejin) or on Discord eejin#4240

## Potential Contributions

Want to help with the development of HiveWE? Below is a list of features that you could implement. You can try one of these or just add something else you feel like HiveWE should have. Any contributions are welcome!

- Being able to change forces/teams
- Changing map sizes/camera bound
- Ramp editing with the terrain palette


If you have any questions then don't be afraid to message me here, on the HiveWorkshop (eejin) or on Discord (eejin)