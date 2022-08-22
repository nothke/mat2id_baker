## Prerequisites
This plugin requires python PIL module. Since Blender may not permit adding modules to its internal folder by default, you'll have to do it manually:

1. Install pillow: `python -m pip install –upgrade Pillow`
2. Copy PIL folder from your python site-packages folder to your blender version's `\python\lib` folder

## How to Use
1. Add bake_mat_to_texture.py as addon in blender
2. Make sure the .blend is saved
3. Select all objects you wish to bake to a single texture (note the name of the final texture will be the name of the ACTIVE object by default)
4. Open the search bar (F3 by default) and search for "mat2id", click on it
5. Now the texture should be created and you'll get a message. You can change parameters after the fact to rebake.

## Additional Notes
Note that the other py files in this repo are not sured, those are just various experiments where I was trying out stuff. I tried making a cython version, which turned out to be tremendously faster, but I couldn't get it to work with blender reliably, so the plugin is actually using a classic python "slow" version