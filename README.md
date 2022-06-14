# **NFT Blender, by** ***Mas***
### **98% Tools for Blender - Not really just for NFTs...** (Web3 support on the "roadmap" 😏)
<br/>

> This package is delivered *as-is*.

## Installation
<!-- todo -->
### Windows
1. Install Blender:
   - [Microsoft Store](https://apps.microsoft.com/store/detail/blender/9PP3C07GTVRH) 
     (recommended for users on shared machine)
   - [MSI Installer](https://www.blender.org/download/)
2. Install Python 3.x:
   - [Microsoft Store](https://apps.microsoft.com/store/detail/python-39/9P7QFQMJRFP7)
     (recommended for users on shared machine)
   - [Application](https://www.python.org/downloads/)
3. Install nft-blender module in Blender:
   1. Launch Blender.
   2. Open the System Console window (Window > Toggle System Console).
   3. Go to the *Scripting* tab.
   4. Copy and run the code in `scripts/install.py` from the [NFT Blender repository](https://github.com/Masangri/nft-blender).<br/>
   5. In the System Console window, copy the Windows path in the last line of the output.
4. Include User's Python installation directory to list of Blender's `site-packages` locations:
   - Create PYTHONPATH environment variable for the user, if it doesn't yet exist.
   - Set the value to the Windows path from the System Console window in step 3.5 above.
5. Close Blender and relaunch.
   - You will now be able to run `import nft_blender` to access scripts.
   - Note that there is no custom menu add-on yet, and scripts will need to be run from the *Scripting* tab by the user.
