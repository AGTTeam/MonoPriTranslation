del monopri_patched.iso
rmdir /s/q patch_temp
wit EXTRACT -o %1 patch_temp
if not exist patch_temp\DATA\ goto scrubbed
xcopy patch\monopri patch_temp\DATA\files /s/e/y/q
xcopy main.dol patch_temp\DATA\sys\main.dol /y/q
goto end
:scrubbed
xcopy patch\monopri patch_temp\files /s/e/y/q
xcopy main.dol patch_temp\sys\main.dol /y/q
:end
wit COPY patch_temp monopri_patched.iso
rmdir /s/q patch_temp
