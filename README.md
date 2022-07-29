# **NFT Blender**
## **98% Tools for Blender...Not really just for NFTs**
A growing set of useful tools for Blender that utilizes the full scope of Python 3 beyond just what ships with Blender, by ***Mas***.<br/>
This module conforms to the requirements of Python packaging, and can be installed **in Blender**, free of dependency issues & user complexity.<br/>
### External libraries include:
- [PySide6](https://pypi.org/project/PySide6/)/[shiboken6](https://pypi.org/project/shiboken6/)
- [PyTest](https://pypi.org/project/pytest/) (dev only)
- [SQLAlchemy](https://pypi.org/project/SQLAlchemy/)
- [Web3](https://pypi.org/project/web3/) (eventually...it's on the "roadmap")

<br/>


> This package is not yet meant for mainstream usage and delivered *as-is*.<br/>
  Several scripts are specilized for custom in-house pipeline(s), but will eventually be made more .<br/>
  If you have ideas and/or run into issues with the module, please contact me! 😎


## Documentation
Documentation generated with readthedocs & Sphinx is deployed on GitHub Pages for this project automatically for every update.*<br/>
To view the latest documentation for using **NFT Blender**, please visit:<br/>
👉 [masangri.github.io/nft-blender](https://masangri.github.io/nft-blender/) 👈

*all credit for CD/CI readthedocs/Sphinx deployment using GitHub actions on GitHub Pages goes to
[Michael Altfield](https://tech.michaelaltfield.net/2020/07/18/sphinx-rtd-github-pages-1)


## Installation
### Windows
1. Install Blender:
   - [Microsoft Store](https://apps.microsoft.com/store/detail/blender/9PP3C07GTVRH) 
     (recommended for users on shared machine)<br/>
     ![README_1](./docs/gfx/README_1.png)
   - [MSI Installer](https://www.blender.org/download/)
2. Install Python 3.x (note: your version may differ from that in the screenshots):
   - [Microsoft Store](https://apps.microsoft.com/store/detail/python-39/9P7QFQMJRFP7)
     (recommended for users on shared machine)<br/>
     ![README_2](./docs/gfx/README_2.png)
   - [Application](https://www.python.org/downloads/)
3. Install nft-blender module in Blender:
   1. Launch Blender.<br/>
      ![README_3_1](./docs/gfx/README_3_1.png)
   2. Open the System Console window (Window > Toggle System Console).<br/>
      ![README_3_2](./docs/gfx/README_3_2.png)
   3. Go to the *Scripting* tab.<br/>
      ![README_3_3](./docs/gfx/README_3_3.png)
   4. Open and run the `nft_blender_install.py` script found in `scripts/` directory of the [NFT Blender repository](https://github.com/Masangri/nft-blender).<br/>
      ![README_3_4](./docs/gfx/README_3_4.png)
   5. In the System Console window, copy the Windows path in the last line of the output.<br/>
      ![README_3_5](./docs/gfx/README_3_5.png)
4. Include User's Python installation directory to list of Blender's `site-packages` locations:
   - Create PYTHONPATH environment variable for the user, if it doesn't yet exist.
   - Set the value to the Windows path from the System Console window in step 3.5 above.<br/>
     ![README_4](./docs/gfx/README_4.png)
5. Close Blender and relaunch.
   - You will now be able to run `import nft_blender` to access the full NFT Blender module.
   - Note that there is no custom menu add-on yet (currently working on it), and scripts will need to be run from the *Scripting* tab by the user.

## Installation for Python Development
- Clone from GitHub:<br/>
  > `git clone https://github.com/Masangri/nft-blender.git && cd nft-blender`
- As a project dependency:<br/>
  > `pip install git+https://github.com/Masangri/nft-blender.git@main#egg=nft-blender`
